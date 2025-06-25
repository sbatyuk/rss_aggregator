import asyncio
import logging
from typing import Optional

import feedparser
import httpx

from rss_aggregator.core.feed import Feed, FEEDS

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

logger = logging.getLogger(__name__)


async def fetch_all_feeds():
    async with httpx.AsyncClient(timeout=10) as client:
        fetch_tasks = [fetch_feed(client, feed) for feed in FEEDS]
        results = await asyncio.gather(*fetch_tasks)

    return results


async def fetch_feed(client: httpx.AsyncClient, feed: Feed) -> tuple[str, Optional[feedparser.FeedParserDict]]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.get(str(feed.url))
            response.raise_for_status()
            parsed = feedparser.parse(response.text)
            return feed.id, parsed
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status >= 500:
                logger.warning(f"[{feed.id}] Server error {status} (attempt {attempt}): {e}")
            else:
                logger.error(f"[{feed.id}] Client error {status}: {e}")
                break
        except httpx.TransportError as e:
            logger.warning(f"[{feed.id}] Transport error (attempt {attempt}): {e}")
        except Exception as e:
            logger.error(f"[{feed.id}] Fatal error: {e}")
            break

        if attempt < MAX_RETRIES:
            await asyncio.sleep(RETRY_DELAY)

    logger.error(f"[{feed.id}] All fetch attempts failed.")
    return feed.id, None
