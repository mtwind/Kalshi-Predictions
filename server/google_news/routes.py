# server/google_news/routes.py
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .news_service import search_news, get_news_analysis

router = APIRouter()


class NewsSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    from_date: Optional[str] = Field(None)
    to_date: Optional[str] = Field(None)
    language: str = Field("en")
    max_results: int = Field(20, ge=1, le=100)
    sort_by: str = Field("publishedAt")

class AnalysisRequest(BaseModel):
    show_name: str = Field(..., description="Show name to analyze")


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

@router.post("/analysis")
def google_news_analysis(req: AnalysisRequest):
    """
    Get a calculated News Score and aggregated metrics.
    """
    return get_news_analysis(req.show_name)