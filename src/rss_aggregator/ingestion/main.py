import asyncio

from rss_aggregator.ingestion import pipeline
from rss_aggregator.logging import setup_logging


async def main():
    setup_logging()

    await pipeline.run()


if __name__ == '__main__':
    asyncio.run(main())
