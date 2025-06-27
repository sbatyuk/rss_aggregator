from typing import Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from rss_aggregator.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=Session)

def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session

def init_db() -> None:
    # Required to register models for SQLModel.metadata
    from rss_aggregator.models import FeedEntry # noqa: F401

    if settings.env == 'dev':
        SQLModel.metadata.drop_all(engine)

    SQLModel.metadata.create_all(engine)