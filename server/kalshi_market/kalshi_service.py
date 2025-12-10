# kalshi_market/kalshi_service.py
from dotenv import load_dotenv
load_dotenv()  # <- make sure this line exists and runs before imports below
import os
import time
import json
import base64
from pathlib import Path
from urllib.parse import urlparse

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

# ---------- Config ----------

BASE_URL = os.getenv(
    "KALSHI_BASE_URL",
    "https://demo-api.kalshi.co/trade-api/v2",
)

API_KEY_ID = os.getenv("KALSHI_API_KEY_ID")
PRIVATE_KEY_PEM = os.getenv("KALSHI_PRIVATE_KEY")
PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH")

# Parse BASE_URL into origin + base path (used in signature)
_parsed = urlparse(BASE_URL)
BASE_ORIGIN = f"{_parsed.scheme}://{_parsed.netloc}"
BASE_PATH_PREFIX = _parsed.path.rstrip("/")  # e.g. "/trade-api/v2"

DATA_DIR = Path("data/kalshi")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Private key loading ----------

_private_key: rsa.RSAPrivateKey | None = None

if PRIVATE_KEY_PATH and API_KEY_ID:
    with open(PRIVATE_KEY_PATH, "rb") as f:
        pem_bytes = f.read()
    _private_key = serialization.load_pem_private_key(
        pem_bytes, password=None, backend=default_backend()
    )
elif PRIVATE_KEY_PEM and API_KEY_ID:
    pem_bytes = PRIVATE_KEY_PEM.encode("utf-8")
    _private_key = serialization.load_pem_private_key(
        pem_bytes, password=None, backend=default_backend()
    )


def _save_json(prefix: str, payload: dict) -> None:
    """Save a JSON snapshot to data/kalshi for debugging."""
    ts = int(time.time() * 1000)
    filename = DATA_DIR / f"{prefix}-{ts}.json"
    try:
        with filename.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        # Logging is best-effort only
        pass


# ---------- Auth helpers ----------

def _sign_message(message: str) -> str:
    """
    Sign a message string with RSA-PSS / SHA256 and return base64 signature.
    If no private key is configured, raises RuntimeError.
    """
    if _private_key is None:
        raise RuntimeError("Kalshi private key not configured")

    signature = _private_key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def _auth_headers(method: str, path: str) -> dict:
    """
    Build KALSHI-ACCESS-* headers for an authenticated request.
    If API keys are not configured, returns an empty dict
    so that public endpoints still work.
    """
    print(f"_private_key: {_private_key}, API_KEY_ID: {API_KEY_ID}")
    if _private_key is None or not API_KEY_ID:
        # No auth configured – caller will hit public endpoints
        print("\n\nNo Authorization\n\n")
        return {}

    ts_ms = int(time.time() * 1000)
    timestamp_str = str(ts_ms)

    # Per docs: sign timestamp + METHOD + path (no query params)
    message = f"{timestamp_str}{method.upper()}{path}"

    signature = _sign_message(message)

    print("\n\nKalshi: using AUTH headers\n\n")

    return {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_str,
        "KALSHI-ACCESS-SIGNATURE": signature,
    }


def _request(method: str, endpoint: str, params: dict | None = None) -> dict:
    """
    Generic request helper.
    `endpoint` is the path segment after the base prefix, e.g. "/markets".
    """
    path = f"{BASE_PATH_PREFIX}{endpoint}"  # e.g. "/trade-api/v2/markets"
    url = f"{BASE_ORIGIN}{path}"

    headers = _auth_headers(method, path)

    resp = requests.request(method, url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ---------- Public functions ----------

def get_event_markets(event_ticker: str, status: str = "open") -> list[dict]:
    """
    Return markets for a Kalshi event. By default only 'open' markets.
    """
    params = {
        "event_ticker": event_ticker,
        "status": status,
        "limit": 1000,
    }
    data = _request("GET", "/markets", params=params)
    markets = data.get("markets", [])

    _save_json(f"markets-{event_ticker}", data)

    return markets


def get_market_orderbook(market_ticker: str) -> dict:
    """
    Return orderbook for a single market.
    """
    data = _request("GET", f"/markets/{market_ticker}/orderbook")

    _save_json(f"orderbook-{market_ticker}", data)

    return data


def _market_sort_key(market: dict) -> float:
    """
    Decide how to rank markets.
    Prefer yes_bid, then last_price, then 0.0.
    """
    return (
        market.get("yes_bid")
        or market.get("last_price")
        or 0.0
    )


def get_top_event_markets(event_ticker: str, limit: int = 5) -> dict:
    """
    Get the top N markets for a given event, sorted by price.
    """
    markets = get_event_markets(event_ticker)
    markets_sorted = sorted(markets, key=_market_sort_key, reverse=True)
    top = markets_sorted[:limit]

    simplified = []
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

    snapshot = {
        "event_ticker": event_ticker,
        "count": len(simplified),
        "markets": simplified,
    }
    _save_json(f"top-markets-{event_ticker}", snapshot)
    return snapshot

def get_top_netflix_markets(limit: int = 5) -> dict:
    """
    Convenience wrapper for the Netflix ranking event.
    """
    snapshot = get_top_event_markets(NETFLIX_EVENT_TICKER, limit=limit)
    _save_json("netflix-top", snapshot)
    return snapshot