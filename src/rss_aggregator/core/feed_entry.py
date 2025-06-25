from datetime import datetime

from sqlmodel import Field, SQLModel


class FeedEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    feed_id: str
    title: str
    url: str
    published_at: datetime
    summary: str | None
