# trends/routes.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Literal

from .trends_service import (
    fetch_interest_single,
    fetch_interest_compare,
    fetch_related,
)

router = APIRouter()

# ---- Models ----
class InterestSingleRequest(BaseModel):
    search_term: str
    start_date: str
    end_date: str
    geo: str = "US"
    category: str = "All"

class InterestCompareRequest(BaseModel):
    search_terms: List[str]
    start_date: str
    end_date: str
    geo: str = "US"
    category: str = "All"

class RelatedRequest(BaseModel):
    search_term: str
    geo: str = "US"
    category: str = "All"
    timeframe: str = "today 12-m"
    mode: Literal["topics", "queries"] = "queries"


# ---- Routes ----

@router.post("/interest")
def interest_single(req: InterestSingleRequest):
    return fetch_interest_single(
        req.search_term, req.start_date, req.end_date, req.geo, req.category
    )


@router.post("/compare")
def interest_compare(req: InterestCompareRequest):
    return fetch_interest_compare(
        req.search_terms, req.start_date, req.end_date, req.geo, req.category
    )


@router.post("/related")
def related(req: RelatedRequest):
    return fetch_related(
        req.search_term, req.geo, req.category, req.timeframe, req.mode
    )
