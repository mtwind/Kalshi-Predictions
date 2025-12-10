# kalshi_market/kalshi_service.py
import os
import requests

BASE_URL = os.getenv(
    "KALSHI_BASE_URL",
    "https://demo-api.kalshi.co/trade-api/v2"
)

def get_event_markets(event_ticker: str):
    """Return all open markets for a Kalshi event."""
    url = f"{BASE_URL}/markets"
    params = {
        "event_ticker": event_ticker,
        "status": "open",
        "limit": 1000,
    }
    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    return r.json().get("markets", [])


def get_market_orderbook(market_ticker: str):
    """Return orderbook for a single market."""
    url = f"{BASE_URL}/markets/{market_ticker}/orderbook"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()
