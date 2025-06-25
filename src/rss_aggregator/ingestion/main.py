import asyncio

from rss_aggregator.core.feed import FEEDS


async def main():
    print(FEEDS)


if __name__ == '__main__':
    asyncio.run(main())
