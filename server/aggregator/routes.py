# server/aggregator/routes.py
from __future__ import annotations

from fastapi import APIRouter
from .aggregator_service import run_full_analysis, get_latest_snapshot

router = APIRouter()

@router.post("/refresh")
def refresh_analysis():
    """
    Triggers a full re-fetch of all data sources.
    This calculates the weighted final score and saves a snapshot.
    """
    return run_full_analysis()

@router.get("/latest")
def get_latest_analysis():
    """
    Returns the most recent analysis snapshot.
    If no snapshot exists, it runs the analysis.
    """
    data = get_latest_snapshot()
    if not data:
        return run_full_analysis()
    return data