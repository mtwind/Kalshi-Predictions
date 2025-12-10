# server/google_news/routes.py
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .news_service import search_news

router = APIRouter()


class NewsSearchRequest(BaseModel):
    query: str = Field(..., description="Search query, e.g. 'Stranger Things Netflix'")
    from_date: Optional[str] = Field(
        default=None,
        description="Optional start date 'YYYY-MM-DD'",
    )
    to_date: Optional[str] = Field(
        default=None,
        description="Optional end date 'YYYY-MM-DD'",
    )
    language: str = Field(
        "en",
        description="2-letter language code, default 'en'",
    )
    max_results: int = Field(
        20,
        ge=1,
        le=100,
        description="Maximum number of articles",
    )
    sort_by: str = Field(
        "publishedAt",
        description="publishedAt | relevance | popularity",
    )


@router.post("/search")
def google_news_search(req: NewsSearchRequest):
    return search_news(
        query=req.query,
        from_date=req.from_date,
        to_date=req.to_date,
        language=req.language,
        max_results=req.max_results,
        sort_by=req.sort_by,
    )
