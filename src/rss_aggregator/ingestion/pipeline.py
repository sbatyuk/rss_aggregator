import logging

from rss_aggregator.ingestion.fetcher import fetch_all_feeds
from rss_aggregator.ingestion.transformer import transform

logger = logging.getLogger(__name__)


async def run():
    raw_feeds = await fetch_all_feeds()

    feed_entries = transform(raw_feeds)

    print(f'Transformed {len(feed_entries)} entries')

    print(feed_entries[0].published_at)
    print(feed_entries[-1].published_at)



