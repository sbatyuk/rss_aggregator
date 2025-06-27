from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from rss_aggregator.db import get_session
from rss_aggregator.models import FeedEntry, FeedEntriesResponse

router = APIRouter(prefix='/entries', tags=['entries'])


@router.get('/', response_model=FeedEntriesResponse)
def list_entries(
        session: Session = Depends(get_session),
        after: datetime | None = Query(None),
        before: datetime | None = Query(None),
        hashtags: list[str] | None = Query(None),
        sort: str = Query('desc', pattern='^(asc|desc)$'),
        limit: int = Query(30, ge=1, le=100)
):
    base_query = select(FeedEntry)
    if after:
        base_query = base_query.where(FeedEntry.published_at > after)
    if before:
        base_query = base_query.where(FeedEntry.published_at < before)

    if hashtags:
        base_query = base_query.where(FeedEntry.hashtags.contains(hashtags))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = session.exec(count_query).one()

    query = base_query
    if sort == "asc":
        query = query.order_by(FeedEntry.published_at.asc())
    else:
        query = query.order_by(FeedEntry.published_at.desc())
    query = query.limit(limit)

    entries = list(session.exec(query).all())

    return FeedEntriesResponse(entries=entries, total=total)
