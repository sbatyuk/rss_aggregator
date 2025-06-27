import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert

from rss_aggregator.db import SessionLocal
from rss_aggregator.models import FeedEntry

logger = logging.getLogger(__name__)


def save(entries: list[FeedEntry]) -> None:
    if not entries:
        logger.info("No feed entries to save.")
        return

    values = [entry.model_dump(exclude_unset=True) for entry in entries]
    stmt = pg_insert(FeedEntry).values(values).on_conflict_do_nothing()

    with SessionLocal() as session:
        session.exec(stmt)
        session.commit()
