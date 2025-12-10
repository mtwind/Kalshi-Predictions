# server/tmdb/routes.py
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .tmdb_service import (
    search_tv_show, 
    get_tv_details, 
    get_trending_tv,
    get_tmdb_analysis # New Import
)

router = APIRouter()


class TVSearchRequest(BaseModel):
    query: str = Field(..., description="TV show name")
    language: str = Field("en-US")
    first_air_date_year: Optional[int] = Field(None)
    page: int = Field(1)

class AnalysisRequest(BaseModel):
    show_name: str = Field(..., description="Show name to analyze")


@router.post("/tv/search")
def tmdb_tv_search(req: TVSearchRequest):
    return search_tv_show(
        query=req.query,
        language=req.language,
        first_air_date_year=req.first_air_date_year,
        page=req.page,
    )


@router.get("/tv/details/{tv_id}")
def tmdb_tv_details(tv_id: int, language: str = "en-US"):
    return get_tv_details(tv_id=tv_id, language=language)


@router.get("/tv/trending")
def tmdb_trending_tv(time_window: str = "day", language: str = "en-US"):
    return get_trending_tv(time_window=time_window, language=language)


@router.post("/analysis")
def tmdb_show_analysis(req: AnalysisRequest):
    """
    Get a calculated score and aggregated metrics for a TV show.
    """
    return get_tmdb_analysis(req.show_name)