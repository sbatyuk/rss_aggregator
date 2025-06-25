import logging

from feedparser import FeedParserDict
from rss_aggregator.core.feed_entry import FeedEntry

logger = logging.getLogger(__name__)


def transform(raw_feeds) -> list[FeedEntry]:
    feed_entries = []

    for feed_id, raw_feed in raw_feeds:
        if not raw_feed:
            logger.warning(f"{feed_id}: failed to fetch or parse")
            continue

        for raw_entry in raw_feed.entries:
            feed_entries.append(transform_raw_entry(feed_id, raw_entry))

    feed_entries = sorted(feed_entries, key=lambda e: e.published_at)

    return feed_entries


def transform_raw_entry(feed_id: str, raw_entry: FeedParserDict) -> FeedEntry:
    return FeedEntry(
        feed_id=feed_id,
        title=raw_entry.title,
        url=raw_entry.link,
        published_at=raw_entry.published_parsed,
        summary=raw_entry.summary
    )
