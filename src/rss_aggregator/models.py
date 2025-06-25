from datetime import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl
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
    url: str
    published_at: datetime
    summary: str | None
