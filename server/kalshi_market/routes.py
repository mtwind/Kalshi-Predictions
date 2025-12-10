# kalshi_market/routes.py
from fastapi import APIRouter
from .kalshi_service import get_event_markets, get_market_orderbook

router = APIRouter()

@router.get("/markets")
def list_markets(event_ticker: str):
    return get_event_markets(event_ticker)

@router.get("/orderbook/{ticker}")
def orderbook(ticker: str):
    return get_market_orderbook(ticker)
