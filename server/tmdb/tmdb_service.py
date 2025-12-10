# server/tmdb/tmdb_service.py
from __future__ import annotations

import json
import os
import math
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
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
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
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()


# ---------- 1) Search TV show ----------

def search_tv_show(
    query: str,
    language: str = "en-US",
    first_air_date_year: Optional[int] = None,
    page: int = 1,
) -> Dict:
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
        "results": data.get("results", []),
    }
    _save_payload(f"search-tv-{_slugify(query)}", payload)
    return payload


# ---------- 2) TV show details ----------

def get_tv_details(tv_id: int, language: str = "en-US") -> Dict:
    params = {"language": language}
    data = _get(f"/tv/{tv_id}", params=params)

    subset = {
        "id": data.get("id"),
        "name": data.get("name"),
        "popularity": data.get("popularity"),
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "first_air_date": data.get("first_air_date"),
        "genres": data.get("genres", []),
    }

    payload = {
        "tv_id": tv_id,
        "summary": subset,
        "raw": data,
    }
    _save_payload(f"tv-details-{tv_id}", payload)
    return payload


# ---------- 3) Trending TV shows ----------

def get_trending_tv(time_window: str = "day", language: str = "en-US") -> Dict:
    data = _get(f"/trending/tv/{time_window}", params={"language": language})
    
    results = data.get("results", [])
    payload = {
        "time_window": time_window,
        "count": len(results),
        "results": results,
    }
    _save_payload(f"trending-tv-{time_window}", payload)
    return payload


# ---------- 4) NEW: Deep Analysis & Score ----------

def get_tmdb_analysis(show_name: str) -> Dict:
    """
    Orchestrates a deep analysis for TMDB:
    1. Search for Show -> Get ID
    2. Fetch Details (Ratings, Pop)
    3. Check Global Trending Status
    4. Calculate 'TMDB Score' (0-100)
    """
    
    # 1. Search
    search_res = search_tv_show(query=show_name)
    results = search_res.get("results", [])
    
    if not results:
        # Return empty/zero stats if not found
        return {
            "name": show_name,
            "found": False,
            "tmdb_score": 0,
            "vote_average": 0,
            "vote_count": 0,
            "popularity": 0,
            "trending_rank": None
        }

    # Assume first result is the best match
    best_match = results[0]
    tv_id = best_match["id"]
    
    # 2. Details
    details_res = get_tv_details(tv_id)
    summary = details_res["summary"]
    
    # 3. Trending Check
    # We fetch the weekly trending list to see if this show is hot right now
    trending_res = get_trending_tv(time_window="week")
    trending_rank = None
    
    for idx, item in enumerate(trending_res.get("results", [])):
        if item["id"] == tv_id:
            trending_rank = idx + 1
            break
            
    # 4. Score Calculation (0-100)
    # A. Rating Score (Max 70): (Vote Average / 10) * 70
    rating_component = (summary.get("vote_average", 0) / 10) * 70
    
    # B. Popularity Score (Max 20): Log scale
    # Pop 100 ~= 10pts, Pop 1000+ ~= 20pts
    pop = summary.get("popularity", 0)
    pop_component = 0
    if pop > 1:
        # log10(100) = 2, log10(1000) = 3. 
        # We want approx 20 pts for viral shows.
        pop_component = min(math.log10(pop) * 6, 20)
        
    # C. Trending Bonus (Max 10)
    trending_bonus = 10 if trending_rank else 0
    
    final_score = rating_component + pop_component + trending_bonus
    
    # Cap at 100 (rare, but possible with massive popularity)
    final_score = min(final_score, 100)

    payload = {
        "name": summary["name"],
        "found": True,
        "tmdb_score": round(final_score, 1),
        "vote_average": round(summary.get("vote_average", 0), 1),
        "vote_count": summary.get("vote_count", 0),
        "popularity": int(summary.get("popularity", 0)),
        "trending_rank": trending_rank,
        "first_air_date": summary.get("first_air_date"),
    }
    
    _save_payload(f"analysis-{_slugify(show_name)}", payload)
    return payload