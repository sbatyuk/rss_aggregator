import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from rss_aggregator.config import settings
from rss_aggregator.ingestion import pipeline
from rss_aggregator.logging import setup_logging


async def main():
    setup_logging()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        pipeline.run,
        "interval",
        minutes=settings.ingestion_interval_minutes,
        next_run_time=datetime.now()  # Run immediately
    )
    scheduler.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
