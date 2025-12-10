# server/youtube/routes.py
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .youtube_service import (
    search_videos,
    get_video_stats,
    get_show_analysis  # Importing the new analysis function
)

router = APIRouter()


# --- Request Models ---

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query, e.g. 'The Witcher trailer'")
    max_results: int = Field(10, ge=1, le=50)
    order: str = Field("relevance", description="relevance | date | viewCount | rating")
    published_after: Optional[str] = Field(
        default=None,
        description="Optional ISO datetime like '2024-01-01T00:00:00Z'",
    )


class StatsRequest(BaseModel):
    video_ids: List[str] = Field(..., description="List of YouTube video IDs")


class TrailerMetricsRequest(BaseModel):
    show_name: str = Field(..., description="Show name, e.g. 'The Witcher'")
    max_results: int = Field(5, ge=1, le=10)


class CommentsRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    max_results: int = Field(50, ge=1, le=100)
    order: str = Field("relevance", description="relevance | time")


class RelatedVideosRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    max_results: int = Field(10, ge=1, le=50)


class AnalysisRequest(BaseModel):
    show_name: str = Field(..., description="Show name to analyze (e.g. 'Stranger Things')")


# --- Routes ---

@router.post("/search")
def youtube_search(req: SearchRequest):
    """
    Search for videos on YouTube.
    """
    return search_videos(
        query=req.query,
        max_results=req.max_results,
        order=req.order,
        published_after=req.published_after,
    )


@router.post("/stats")
def youtube_stats(req: StatsRequest):
    """
    Get detailed statistics (views, likes, comments) for a list of video IDs.
    """
    return get_video_stats(req.video_ids)


@router.post("/trailer-metrics")
def youtube_trailer_metrics(req: TrailerMetricsRequest):
    """
    Convenience endpoint: Find trailers for a show and get their stats.
    """
    return get_trailer_metrics(req.show_name, max_results=req.max_results)


@router.post("/comments")
def youtube_comments(req: CommentsRequest):
    """
    Get top-level comments for a video.
    """
    return get_video_comments(
        video_id=req.video_id,
        max_results=req.max_results,
        order=req.order,
    )


@router.post("/related")
def youtube_related(req: RelatedVideosRequest):
    """
    Get videos related to a given video.
    """
    return get_related_videos(
        video_id=req.video_id,
        max_results=req.max_results,
    )


@router.post("/analysis")
def youtube_analysis(req: AnalysisRequest):
    """
    Perform deep analysis: Avg stats, Trailer stats, and Comment Sentiment.
    This aggregates multiple API calls into one response for the dashboard.
    """
    return get_show_analysis(req.show_name)