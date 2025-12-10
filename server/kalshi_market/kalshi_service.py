# kalshi_market/kalshi_service.py
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

# Use the Production URL by default for real data, or Demo if explicitly set
# Production: https://api.elections.kalshi.com/trade-api/v2
# Demo:       https://demo-api.kalshi.co/trade-api/v2
BASE_URL = os.getenv(
    "KALSHI_BASE_URL",
    "https://api.elections.kalshi.com/trade-api/v2",
)

API_KEY_ID = os.getenv("KALSHI_API_KEY_ID")
PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH")

# Parse URL to separate Host (Origin) from Path (Prefix)
# This ensures we sign the correct path segments regardless of how the env var is formatted.
_parsed = urlparse(BASE_URL)
BASE_HOST = f"{_parsed.scheme}://{_parsed.netloc}"  # e.g., https://api.elections.kalshi.com
BASE_PATH_PREFIX = _parsed.path.rstrip("/")        # e.g., /trade-api/v2

# Local data storage
DATA_DIR = Path("data/kalshi")
DATA_DIR.mkdir(parents=True, exist_ok=True)

NETFLIX_EVENT_TICKER = os.getenv("NETFLIX_EVENT_TICKER", "KXNETFLIXRANKSHOW-25DEC15")


# ---------------------------------------------------------------------------
# Authentication Helpers (From Kalshi Docs)
# ---------------------------------------------------------------------------

def load_private_key_from_file(file_path):
    """
    Load the private key stored in a file.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"Warning: Private key not found at {file_path}")
        return None
        
    try:
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # provide password here if key is encrypted
                backend=default_backend()
            )
        return private_key
    except Exception as e:
        print(f"Error loading private key: {e}")
        return None

def sign_pss_text(private_key: rsa.RSAPrivateKey, text: str) -> str:
    """
    Sign text with private key using RSA-PSS.
    """
    message = text.encode('utf-8')
    try:
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    except InvalidSignature as e:
        raise ValueError("RSA sign PSS failed") from e

# Initialize the key once on module load
_private_key = load_private_key_from_file(PRIVATE_KEY_PATH)


# ---------------------------------------------------------------------------
# Request Logic
# ---------------------------------------------------------------------------

def _request(method: str, endpoint: str, params: dict | None = None) -> dict:
    """
    Internal helper to make authenticated requests to Kalshi.
    
    Args:
        method: "GET", "POST", etc.
        endpoint: The API path relative to the version prefix (e.g., "/markets")
        params: Query parameters dict
    """
    # 1. Construct the full path and URL
    #    endpoint should start with /, e.g. /portfolio/balance
    full_path = f"{BASE_PATH_PREFIX}{endpoint}" # e.g. /trade-api/v2/markets
    url = f"{BASE_HOST}{full_path}"

    headers = {}

    # 2. Build Authentication Headers (if key is present)
    if _private_key and API_KEY_ID:
        # Generate timestamps
        current_time = datetime.datetime.now()
        timestamp_float = current_time.timestamp()
        timestamp_ms_str = str(int(timestamp_float * 1000))
        
        # Path for signing must NOT have query params
        # In this flow, 'full_path' does not contain params (requests adds them later)
        path_to_sign = full_path.split('?')[0]

        # Sign: timestamp + method + path
        msg_string = timestamp_ms_str + method.upper() + path_to_sign
        
        try:
            signature = sign_pss_text(_private_key, msg_string)
            headers = {
                "KALSHI-ACCESS-KEY": API_KEY_ID,
                "KALSHI-ACCESS-SIGNATURE": signature,
                "KALSHI-ACCESS-TIMESTAMP": timestamp_ms_str,
                "Content-Type": "application/json"
            }
        except Exception as e:
            print(f"Signing failed: {e}")
    else:
        print("Notice: Missing API Key or Private Key. Attempting unauthenticated request.")

    # 3. Send Request
    try:
        # print(f"DEBUG Request: {method} {url} | Params: {params}") # Uncomment for debug
        resp = requests.request(method, url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"\n[Kalshi API Error] {e}")
        print(f"Response Body: {resp.text}\n")
        raise e
    except Exception as e:
        print(f"Request failed: {e}")
        return {}


def _save_json(prefix: str, payload: dict) -> None:
    """Save a JSON snapshot to data/kalshi for debugging/history."""
    ts = int(time.time() * 1000)
    filename = DATA_DIR / f"{prefix}-{ts}.json"
    try:
        with filename.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Public Endpoints
# ---------------------------------------------------------------------------

def get_event_markets(event_ticker: str, status: str = "open") -> list[dict]:
    """
    Return markets for a Kalshi event.
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
    Helper to rank markets by 'yes_bid' or 'last_price'.
    """
    return (
        market.get("yes_bid")
        or market.get("last_price")
        or 0.0
    )


def get_top_event_markets(event_ticker: str, limit: int = 5) -> dict:
    """
    Get the top N markets for a given event, sorted by highest 'Yes' price.
    """
    markets = get_event_markets(event_ticker)
    
    # Sort descending by price
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