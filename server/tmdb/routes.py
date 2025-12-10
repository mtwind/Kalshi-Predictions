# server/tmdb/routes.py
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .tmdb_service import search_tv_show, get_tv_details, get_trending_tv

router = APIRouter()


class TVSearchRequest(BaseModel):
    query: str = Field(..., description="TV show name, e.g. 'Stranger Things'")
    language: str = Field("en-US", description="Language code, e.g. 'en-US'")
    first_air_date_year: Optional[int] = Field(
        default=None,
        description="Optional year of first air date to disambiguate titles",
    )
    page: int = Field(1, ge=1, le=1000, description="Result page number")


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
    """
    time_window: 'day' or 'week'
    """
    return get_trending_tv(time_window=time_window, language=language)
