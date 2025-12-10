# server/aggregator/routes.py
from __future__ import annotations

from fastapi import APIRouter
from .aggregator_service import run_full_analysis, get_latest_snapshot, recalculate_scores

router = APIRouter()

@router.post("/refresh")
def refresh_analysis():
    """
    Full Refetch: Calls APIs (expensive) + Calculates Scores.
    """
    return run_full_analysis()

@router.post("/recalculate")
def recalculate_analysis():
    """
    Quick Recalc: Loads cached data + Re-runs scoring algorithm (cheap).
    Use this when tuning weights or edge logic.
    """
    return recalculate_scores()

@router.get("/latest")
def get_latest_analysis():
    """
    Returns the most recent snapshot.
    """
    data = get_latest_snapshot()
    if not data:
        return run_full_analysis()
    return data