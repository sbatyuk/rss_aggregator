import calendar
import datetime
import html
import logging
import time

from feedparser import FeedParserDict
from slugify import slugify
from sqlalchemy import select, func

from rss_aggregator.db import SessionLocal
from rss_aggregator.models import FeedEntry
from rss_aggregator.nlp import embedder, keyword_extractor

logger = logging.getLogger(__name__)


def transform(raw_feeds) -> list[FeedEntry]:
    latest_published_at = get_latest_published_at_per_feed()
    feed_entries = []
    feed_entries_without_hashtags = []

    for feed_id, raw_feed in raw_feeds:
        if not raw_feed:
            logger.warning(f"{feed_id}: failed to fetch or parse")
            continue

        for raw_entry in raw_feed.entries:
            try:
                feed_entry = transform_raw_entry(feed_id, raw_entry)
                if feed_id not in latest_published_at or feed_entry.published_at >= latest_published_at[feed_id]:
                    feed_entries.append(feed_entry)
                    if not feed_entry.hashtags:
                        feed_entries_without_hashtags.append(feed_entry)
            except Exception:
                logger.exception(f"Failed to process entry (link={feed_entry.link}) from feed '{feed_id}'")

    try:
        add_hashtags(feed_entries_without_hashtags)
    except Exception:
        logger.exception('Failed to add hashtags')

    try:
        add_embeddings(feed_entries)
    except Exception:
        logger.exception('Failed to add embeddings')

    feed_entries = sorted(feed_entries, key=lambda e: e.published_at)

    return feed_entries


def transform_raw_entry(feed_id: str, raw_entry: FeedParserDict) -> FeedEntry:
    return FeedEntry(
        feed_id=feed_id,
        title=html.unescape(raw_entry.title),
        link=raw_entry.link,
        published_at=struct_time_to_datetime(raw_entry.published_parsed),
        summary=html.unescape(raw_entry.summary),
        hashtags=normalize_tags(raw_entry.get('tags', []))
    )


def get_latest_published_at_per_feed() -> dict[str, datetime.datetime]:
    with SessionLocal() as session:
        stmt = (
            select(FeedEntry.feed_id, func.max(FeedEntry.published_at))
            .group_by(FeedEntry.feed_id)
        )
        results = session.exec(stmt).all()
        return {feed_id: published_at for feed_id, published_at in results}


def struct_time_to_datetime(struct_time: time.struct_time) -> datetime:
    return datetime.datetime.fromtimestamp(calendar.timegm(struct_time), datetime.UTC)


def normalize_tags(raw_tags: list[dict]) -> list[str]:
    return [slugify(tag['term']) for tag in raw_tags if tag.get('term')]


def add_hashtags(feed_entries) -> None:
    texts = feed_entries_to_texts(feed_entries)
    keywords = keyword_extractor.extract_keywords(texts, top_n=3)
    if len(feed_entries) == 1:
        keywords = [keywords]

    for feed_entry, hashtags in zip(feed_entries, keywords):
        feed_entry.hashtags = [slugify(ht) for ht, _ in hashtags]


def add_embeddings(feed_entries):
    texts = feed_entries_to_texts(feed_entries)
    embeddings = embedder.encode(texts)
    for feed_entry, embedding in zip(feed_entries, embeddings):
        feed_entry.embedding = embedding


def feed_entries_to_texts(feed_entries):
    return [f"{entry.title}. {entry.summary}" for entry in feed_entries]
