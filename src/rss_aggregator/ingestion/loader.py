import logging

from rss_aggregator.db import SessionLocal
from rss_aggregator.models import FeedEntry

logger = logging.getLogger(__name__)


def save(entries: list[FeedEntry]) -> None:
    if not entries:
        logger.info("No feed entries to save.")
        return

    with SessionLocal() as session:
        session.add_all(entries)
        session.commit()
        logger.info(f"Saved {len(entries)} feed entries.")
