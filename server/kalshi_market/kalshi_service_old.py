# kalshi_market/kalshi_service.py
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = os.getenv(
    "KALSHI_BASE_URL",
    "https://demo-api.kalshi.co/trade-api/v2",
)

# Default Netflix event ticker (override in .env if needed)
NETFLIX_EVENT_TICKER = os.getenv(
    "NETFLIX_EVENT_TICKER",
    "KXNETFLIXRANKSHOW-25DEC15",  # change if your event ticker is different
)

# Where to store raw + processed Kalshi payloads
DATA_DIR = Path("data/kalshi")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _save_payload(prefix: str, payload: Dict[str, Any]) -> str:
    """
    Save a JSON payload under data/kalshi with a timestamped filename.
    Returns the file path as a string.
    """
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}-{ts}.json"
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)


# ---------------------------------------------------------------------------
# Core API wrappers
# ---------------------------------------------------------------------------

def get_event_markets(event_ticker: str) -> Dict[str, Any]:
    """
    Return all open markets for a Kalshi event.

    Response format:
    {
        "event_ticker": "...",
        "count": <int>,
        "markets": [ ...raw market objects from Kalshi... ]
    }
    """
    url = f"{BASE_URL}/markets"
    params = {
        "event_ticker": event_ticker,
        "status": "open",
        "limit": 1000,
    }
    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    raw = r.json()

    # Save the full raw response
    _save_payload(f"markets-{event_ticker}", raw)

    markets: List[Dict[str, Any]] = raw.get("markets", [])
    return {
        "event_ticker": event_ticker,
        "count": len(markets),
        "markets": markets,
    }


def get_market_orderbook(market_ticker: str) -> Dict[str, Any]:
    """
    Return orderbook for a single market (raw Kalshi format).
    """
    url = f"{BASE_URL}/markets/{market_ticker}/orderbook"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    raw = r.json()

    _save_payload(f"orderbook-{market_ticker}", raw)
    return raw


# ---------------------------------------------------------------------------
# Helpers for "top markets" (e.g., Netflix top shows)
# ---------------------------------------------------------------------------

def _market_sort_key(market: Dict[str, Any]) -> float:
    """
    Decide how to rank markets.
    Prefer yes_bid, then last_price, then 0.0.
    Adjust as needed if your schema uses different fields.
    """
    return (
        market.get("yes_bid")
        or market.get("last_price")
        or 0.0
    )


def get_top_event_markets(event_ticker: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get the top N markets for a given event, sorted by price.
    Returns a simplified structure and saves a snapshot to data/kalshi.
    """
    base = get_event_markets(event_ticker)
    markets: List[Dict[str, Any]] = base.get("markets", [])

    markets_sorted = sorted(markets, key=_market_sort_key, reverse=True)
    top = markets_sorted[:limit]

    simplified: List[Dict[str, Any]] = []
    for m in top:
        simplified.append(
            {
                "ticker": m.get("ticker"),
                "title": m.get("title") or m.get("name"),
                "yes_bid": m.get("yes_bid"),
                "yes_ask": m.get("yes_ask"),
                "no_bid": m.get("no_bid"),
                "no_ask": m.get("no_ask"),
                "last_price": m.get("last_price"),
                "volume": m.get("volume"),
                "open_interest": m.get("open_interest"),
                "event_ticker": m.get("event_ticker"),
            }
        )

    payload = {
        "event_ticker": event_ticker,
        "count": len(simplified),
        "markets": simplified,
        "raw_markets": markets,
        "sorted_markets": markets_sorted[:limit],
    }

    _save_payload(f"top-markets-{event_ticker}", payload)
    return payload


def get_top_netflix_markets(limit: int = 5) -> Dict[str, Any]:
    """
    Convenience wrapper for the configured Netflix ranking event.
    """
    payload = get_top_event_markets(NETFLIX_EVENT_TICKER, limit=limit)
    _save_payload("netflix-top", payload)
    return payload
