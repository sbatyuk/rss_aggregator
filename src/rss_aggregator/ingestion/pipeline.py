from rss_aggregator.ingestion.fetcher import fetch_all_feeds
from rss_aggregator.ingestion.loader import save
from rss_aggregator.ingestion.transformer import transform


async def run():
    raw_feeds = await fetch_all_feeds()
    feed_entries = transform(raw_feeds)
    save(feed_entries)
