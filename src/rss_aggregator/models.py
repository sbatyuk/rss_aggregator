from datetime import datetime
from pathlib import Path

import yaml
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, HttpUrl
from sqlalchemy import Column, DateTime, Index, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field

from rss_aggregator.config import FEEDS_PATH


class Feed(BaseModel):
    id: str
    url: HttpUrl


def load_feeds(path: Path = FEEDS_PATH) -> list[Feed]:
    with path.open("r") as f:
        data = yaml.safe_load(f)
    return [Feed(**entry) for entry in data.get("feeds", [])]


FEEDS = load_feeds()


class FeedEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    feed_id: str
    title: str
    link: str = Field(unique=True)
    published_at: datetime = Field(sa_column=Column(DateTime(timezone=True), index=True, nullable=False))
    summary: str
    hashtags: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    embedding: list[float] | None = Field(sa_column=Column(Vector(384)), exclude=True)

    __table_args__ = (
        Index('ix_feedentry_feed_id_published_at', 'feed_id', 'published_at'),
    )


class FeedEntriesResponse(BaseModel):
    entries: list[FeedEntry]
    total: int
