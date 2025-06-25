import asyncio

from rss_aggregator.ingestion.fetcher import fetch_all_feeds
from rss_aggregator.util.logging import setup_logging


async def main():
    setup_logging()

    results = await fetch_all_feeds()
    for feed_id, parsed_feed in results:
        if parsed_feed:
            print(f"{feed_id}: {len(parsed_feed.entries)} entries")
        else:
            print(f"{feed_id}: failed to fetch or parse")


if __name__ == '__main__':
    asyncio.run(main())
