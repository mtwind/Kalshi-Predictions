# server/tmdb/tmdb_service.py
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from fastapi import HTTPException

DATA_DIR = Path("data/tmdb")
DATA_DIR.mkdir(parents=True, exist_ok=True)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


def _require_api_key() -> str:
    if not TMDB_API_KEY:
        raise RuntimeError("TMDB_API_KEY not set in environment")
    return TMDB_API_KEY


def _slugify(value: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-")


def _save_payload(prefix: str, payload: dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}-{ts}.json"
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)


def _get(path: str, params: Optional[Dict] = None) -> Dict:
    api_key = _require_api_key()
    url = f"{TMDB_BASE_URL}{path}"
    params = params or {}
    params["api_key"] = api_key

    r = requests.get(url, params=params, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        # Bubble TMDB's error up
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()


# ---------- 1) Search TV show ----------

def search_tv_show(
    query: str,
    language: str = "en-US",
    first_air_date_year: Optional[int] = None,
    page: int = 1,
) -> Dict:
    """
    Search TV shows by name.
    Returns TMDB's search results; each result contains id, name, popularity, etc.
    """
    params: Dict = {
        "query": query,
        "language": language,
        "page": page,
        "include_adult": False,
    }
    if first_air_date_year is not None:
        params["first_air_date_year"] = first_air_date_year

    data = _get("/search/tv", params=params)

    payload = {
        "query": query,
        "language": language,
        "first_air_date_year": first_air_date_year,
        "page": page,
        "total_results": data.get("total_results", 0),
        "results": data.get("results", []),
        "raw": data,
    }

    _save_payload(f"search-tv-{_slugify(query)}", payload)
    return payload


# ---------- 2) TV show details ----------

def get_tv_details(tv_id: int, language: str = "en-US") -> Dict:
    """
    Get details for a TV show by TMDB id.
    Contains popularity, vote_average, vote_count, genres, etc.
    """
    params = {"language": language}
    data = _get(f"/tv/{tv_id}", params=params)

    # pull out a normalized subset plus the full raw object
    subset = {
        "id": data.get("id"),
        "name": data.get("name"),
        "original_name": data.get("original_name"),
        "overview": data.get("overview"),
        "first_air_date": data.get("first_air_date"),
        "popularity": data.get("popularity"),
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "number_of_seasons": data.get("number_of_seasons"),
        "number_of_episodes": data.get("number_of_episodes"),
        "genres": data.get("genres", []),
        "origin_country": data.get("origin_country", []),
    }

    payload = {
        "tv_id": tv_id,
        "language": language,
        "summary": subset,
        "raw": data,
    }

    _save_payload(f"tv-details-{tv_id}", payload)
    return payload


# ---------- 3) Trending TV shows ----------

def get_trending_tv(time_window: str = "day", language: str = "en-US") -> Dict:
    """
    Get trending TV shows.
    time_window: "day" or "week"
    """
    data = _get(f"/trending/tv/{time_window}", params={"language": language})

    payload = {
        "time_window": time_window,
        "language": language,
        "count": len(data.get("results", [])),
        "results": data.get("results", []),
        "raw": data,
    }

    _save_payload(f"trending-tv-{time_window}", payload)
    return payload
