import calendar
import datetime
import logging
import time

from feedparser import FeedParserDict
from slugify import slugify
from sqlalchemy import select, func

from rss_aggregator.db import SessionLocal
from rss_aggregator.embedding import embedder
from rss_aggregator.models import FeedEntry

logger = logging.getLogger(__name__)


def transform(raw_feeds) -> list[FeedEntry]:
    latest_published_at = get_latest_published_at_per_feed()
    feed_entries = []

    for feed_id, raw_feed in raw_feeds:
        if not raw_feed:
            logger.warning(f"{feed_id}: failed to fetch or parse")
            continue

        for raw_entry in raw_feed.entries:
            try:
                feed_entry = transform_raw_entry(feed_id, raw_entry)
                if feed_id not in latest_published_at or feed_entry.published_at >= latest_published_at[feed_id]:
                    enrich_feed_entry(raw_entry, feed_entry)
                    feed_entries.append(feed_entry)
            except Exception as e:
                logger.exception(f"Failed to process entry (link={feed_entry.link}) from feed '{feed_id}': {e}")

    feed_entries = sorted(feed_entries, key=lambda e: e.published_at)

    return feed_entries


def transform_raw_entry(feed_id: str, raw_entry: FeedParserDict) -> FeedEntry:
    return FeedEntry(
        feed_id=feed_id,
        title=raw_entry.title,
        link=raw_entry.link,
        published_at=struct_time_to_datetime(raw_entry.published_parsed),
        summary=raw_entry.summary
    )


def enrich_feed_entry(raw_entry: FeedParserDict, feed_entry: FeedEntry) -> None:
    feed_entry.hashtags = normalize_tags(raw_entry.get('tags', []))
    feed_entry.embedding = embedder.encode(f'{feed_entry.title}. {feed_entry.summary}').tolist()


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
