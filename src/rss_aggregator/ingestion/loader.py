import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert

from rss_aggregator.db import SessionLocal
from rss_aggregator.models import FeedEntry

logger = logging.getLogger(__name__)


def save(entries: list[FeedEntry]) -> None:
    if not entries:
        logger.info("No feed entries to save.")
        return

    values = [{**entry.model_dump(exclude_unset=True), 'embedding': entry.embedding} for entry in entries]
    stmt = pg_insert(FeedEntry).values(values).on_conflict_do_nothing().returning(FeedEntry.id)

    with SessionLocal() as session:
        result = session.exec(stmt)
        inserted_count = len(result.all())
        session.commit()

    logger.info(f"Inserted {inserted_count} new entries.")
