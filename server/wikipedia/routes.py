# server/wikipedia/routes.py
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .wikipedia_service import get_pageviews_daily

router = APIRouter()


class PageviewsRequest(BaseModel):
    article_title: str = Field(
        ...,
        description="Wikipedia page title, e.g. 'Stranger_Things' (use underscores instead of spaces).",
    )
    start_date: str = Field(
        ...,
        description="Start date in 'YYYY-MM-DD' format, e.g. '2024-01-01'.",
    )
    end_date: str = Field(
        ...,
        description="End date in 'YYYY-MM-DD' format, e.g. '2024-02-01'.",
    )
    project: str = Field(
        "en.wikipedia",
        description="Wikimedia project, default 'en.wikipedia'.",
    )
    access: str = Field(
        "all-access",
        description="Access channel: all-access | desktop | mobile-web | mobile-app",
    )
    agent: str = Field(
        "all-agents",
        description="Agent type: all-agents | user | spider | automated",
    )


@router.post("/pageviews")
def wikipedia_pageviews(req: PageviewsRequest):
    return get_pageviews_daily(
        article_title=req.article_title,
        start_date=req.start_date,
        end_date=req.end_date,
        project=req.project,
        access=req.access,
        agent=req.agent,
    )
