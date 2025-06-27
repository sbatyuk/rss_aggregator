from fastapi import FastAPI
from rss_aggregator.api.entries import router as entries_router

app = FastAPI(
    title="RSS Aggregator API",
    version="0.1",
    description="API for listing and searching RSS feed entries."
)

app.include_router(entries_router, prefix="/api")