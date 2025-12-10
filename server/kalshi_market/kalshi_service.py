# server/kalshi_market/kalshi_service.py
import os
import time
import json
import base64
import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

load_dotenv()

# ---------------------------------------------------------------------------
# Config & Setup
# ---------------------------------------------------------------------------

BASE_URL = os.getenv(
    "KALSHI_BASE_URL",
    "https://api.elections.kalshi.com/trade-api/v2",
)

API_KEY_ID = os.getenv("KALSHI_API_KEY_ID")
PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH")

_parsed = urlparse(BASE_URL)
BASE_HOST = f"{_parsed.scheme}://{_parsed.netloc}"
BASE_PATH_PREFIX = _parsed.path.rstrip("/")

DATA_DIR = Path("data/kalshi")
DATA_DIR.mkdir(parents=True, exist_ok=True)

NETFLIX_EVENT_TICKER = os.getenv("NETFLIX_EVENT_TICKER", "KXNETFLIXRANKSHOW-25DEC15")


# ---------------------------------------------------------------------------
# Authentication Helpers
# ---------------------------------------------------------------------------

def load_private_key_from_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )
    except Exception as e:
        print(f"Error loading private key: {e}")
        return None

def sign_pss_text(private_key: rsa.RSAPrivateKey, text: str) -> str:
    try:
        signature = private_key.sign(
            text.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    except InvalidSignature as e:
        raise ValueError("RSA sign PSS failed") from e

_private_key = load_private_key_from_file(PRIVATE_KEY_PATH)


# ---------------------------------------------------------------------------
# Request Logic
# ---------------------------------------------------------------------------

def _request(method: str, endpoint: str, params: dict | None = None) -> dict:
    full_path = f"{BASE_PATH_PREFIX}{endpoint}"
    url = f"{BASE_HOST}{full_path}"
    headers = {}

    if _private_key and API_KEY_ID:
        ts = str(int(datetime.datetime.now().timestamp() * 1000))
        msg = ts + method.upper() + full_path.split('?')[0]
        try:
            sig = sign_pss_text(_private_key, msg)
            headers = {
                "KALSHI-ACCESS-KEY": API_KEY_ID,
                "KALSHI-ACCESS-SIGNATURE": sig,
                "KALSHI-ACCESS-TIMESTAMP": ts,
                "Content-Type": "application/json"
            }
        except Exception as e:
            print(f"Signing failed: {e}")

    try:
        resp = requests.request(method, url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"Kalshi Error: {e.response.text}")
        raise e
    except Exception:
        return {}

def _save_json(prefix: str, payload: dict) -> None:
    try:
        ts = int(time.time() * 1000)
        with (DATA_DIR / f"{prefix}-{ts}.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Public Functions
# ---------------------------------------------------------------------------

def get_event_markets(event_ticker: str, status: str = "open") -> list[dict]:
    data = _request("GET", "/markets", params={"event_ticker": event_ticker, "status": status, "limit": 1000})
    markets = data.get("markets", [])
    _save_json(f"markets-{event_ticker}", data)
    return markets

def get_market_orderbook(market_ticker: str) -> dict:
    data = _request("GET", f"/markets/{market_ticker}/orderbook")
    _save_json(f"orderbook-{market_ticker}", data)
    return data

def _market_sort_key(market: dict) -> float:
    # Rank by implied probability (Chance)
    # Priority: Last Traded Price -> Best Bid -> 0
    return market.get("last_price") or market.get("yes_bid") or 0.0

def get_top_event_markets(event_ticker: str, limit: int = 5) -> dict:
    markets = get_event_markets(event_ticker)
    
    # Sort by chance (highest first) using the updated sort key
    markets_sorted = sorted(markets, key=_market_sort_key, reverse=True)
    top = markets_sorted[:limit]

    simplified = []
    for m in top:
        # Calculate chance based on 'how much YES recently traded for'
        chance = m.get("last_price") or m.get("yes_bid") or 0
        
        simplified.append({
            "ticker": m.get("ticker"),
            "title": m.get("title"),
            "subtitle": m.get("subtitle"),  # The clean show name (e.g. "Stranger Things 5")
            "chance": chance,               # The calculated probability percentage
            "yes_bid": m.get("yes_bid"),
            "yes_ask": m.get("yes_ask"),
            "no_bid": m.get("no_bid"),
            "no_ask": m.get("no_ask"),
            "last_price": m.get("last_price"),
            "volume": m.get("volume"),
            "event_ticker": m.get("event_ticker"),
        })

    snapshot = {
        "event_ticker": event_ticker,
        "count": len(simplified),
        "markets": simplified,
    }
    _save_json(f"top-markets-{event_ticker}", snapshot)
    return snapshot

def get_top_netflix_markets(limit: int = 5) -> dict:
    snapshot = get_top_event_markets(NETFLIX_EVENT_TICKER, limit=limit)
    _save_json("netflix-top", snapshot)
    return snapshot