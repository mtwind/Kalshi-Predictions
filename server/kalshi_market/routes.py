# kalshi_market/routes.py
from fastapi import APIRouter, Query
from typing import Optional

from .kalshi_service import (
    get_event_markets,
    get_market_orderbook,
    get_top_event_markets,
    get_top_netflix_markets,
)

router = APIRouter()


# ------------------------------------------------------------
# BASIC ENDPOINTS (existing)
# ------------------------------------------------------------

@router.get("/markets")
def list_markets(event_ticker: str = Query(..., description="Kalshi event ticker")):
    """
    Return all open markets for the given event.
    Data is saved automatically under data/kalshi/.
    """
    return get_event_markets(event_ticker)


@router.get("/orderbook/{ticker}")
def orderbook(ticker: str):
    """
    Return orderbook for a specific Kalshi market.
    Also written to data/kalshi/.
    """
    return get_market_orderbook(ticker)


# ------------------------------------------------------------
# NEW ENDPOINTS — TOP MARKETS
# ------------------------------------------------------------

@router.get("/top_markets")
def top_markets(
    event_ticker: str = Query(..., description="Kalshi event ticker"),
    limit: int = Query(5, description="Number of markets to return"),
):
    """
    Return the top N markets for a given event (sorted by yes_bid/last_price)
    and save the result in data/kalshi/.
    """
    return get_top_event_markets(event_ticker, limit=limit)


# ------------------------------------------------------------
# NEW ENDPOINTS — NETFLIX CONVENIENCE ROUTES
# ------------------------------------------------------------

@router.get("/netflix/top")
def netflix_top_markets(limit: int = Query(5, description="Top N Netflix markets")):
    """
    Shortcut for the Netflix ranking event.
    Uses NETFLIX_EVENT_TICKER configured in environment or defaults.
    Saves output automatically.
    """
    return get_top_netflix_markets(limit=limit)


@router.get("/netflix/orderbooks")
def netflix_orderbooks(limit: int = Query(5, description="Number of top Netflix markets to fetch orderbooks for")):
    """
    Returns orderbooks for the top N Netflix markets.
    Useful when you need depth data for ranking-based prediction.
    Saves all orderbooks to data/kalshi/.
    """
    top = get_top_netflix_markets(limit=limit)

    tickers = [m["ticker"] for m in top["markets"] if m.get("ticker")]
    orderbooks = {}

    for t in tickers:
        try:
            orderbooks[t] = get_market_orderbook(t)
        except Exception as e:
            orderbooks[t] = {"error": str(e)}

    return {
        "event_ticker": top["event_ticker"],
        "count": len(orderbooks),
        "orderbooks": orderbooks,
    }
