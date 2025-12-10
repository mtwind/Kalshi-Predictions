# server/aggregator/aggregator_service.py
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Import existing services
from kalshi_market.kalshi_service import get_event_markets, NETFLIX_EVENT_TICKER, _market_sort_key
from youtube.youtube_service import get_show_analysis
from google_news.news_service import get_news_analysis
from tmdb.tmdb_service import get_tmdb_analysis
from wikipedia.wikipedia_service import get_pageviews_daily

DATA_DIR = Path("data/full-analysis")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _save_snapshot(payload: dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"analysis-snapshot-{ts}.json"
    path = DATA_DIR / filename
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving snapshot: {e}")
    return str(path)


def get_latest_snapshot() -> Dict:
    try:
        files = sorted(DATA_DIR.glob("analysis-snapshot-*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if files:
            with files[0].open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def normalize_show_name(raw_name: str) -> str:
    if not raw_name: return ""
    name = raw_name
    parts = re.split(r":\s*Season", name, flags=re.IGNORECASE)
    name = parts[0]
    name = re.sub(r"\s+\d+$", "", name)
    return name.strip()


def run_full_analysis() -> Dict:
    print("Starting full analysis...")

    # 1. Get Full Kalshi Data
    all_markets = get_event_markets(NETFLIX_EVENT_TICKER)
    markets_sorted = sorted(all_markets, key=_market_sort_key, reverse=True)
    top_markets = markets_sorted[:5]
    
    collected_data = []
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    date_fmt = "%Y-%m-%d"
    
    grand_total_wiki_views = 0

    # --- Phase 1: Fetch Data ---
    for market in top_markets:
        raw_show_name = market.get("subtitle")
        if not raw_show_name:
            continue
            
        clean_show_name = normalize_show_name(raw_show_name)
        print(f"Aggregating data for: {raw_show_name} -> '{clean_show_name}'")
        
        # 1. Kalshi (50%)
        chance = market.get("last_price") or market.get("yes_bid") or 0
        kalshi_score = float(chance)

        # 2. YouTube (20%)
        try:
            yt_data = get_show_analysis(clean_show_name)
            # Extract score from the new 'totals' object
            yt_score = float(yt_data.get("totals", {}).get("youtube_score", 0))
        except Exception as e:
            print(f"Error fetching YouTube for {clean_show_name}: {e}")
            yt_data = {"totals": {}, "videos": []}
            yt_score = 0.0

        # 3. News (15%)
        try:
            news_data = get_news_analysis(clean_show_name)
            news_score = float(news_data.get("news_score", 0))
        except Exception as e:
            print(f"Error fetching News for {clean_show_name}: {e}")
            news_data = {}
            news_score = 0.0

        # 4. TMDB (10%)
        try:
            tmdb_data = get_tmdb_analysis(clean_show_name)
            tmdb_score = float(tmdb_data.get("tmdb_score", 0))
        except Exception as e:
            print(f"Error fetching TMDB for {clean_show_name}: {e}")
            tmdb_data = {}
            tmdb_score = 0.0

        # 5. Wikipedia (5%)
        wiki_article_title = clean_show_name.replace(" ", "_")
        try:
            wiki_data = get_pageviews_daily(
                article_title=wiki_article_title, 
                start_date=start_date.strftime(date_fmt),
                end_date=end_date.strftime(date_fmt)
            )
            points = wiki_data.get("points", [])
            total_views = sum(p["views"] for p in points)
            grand_total_wiki_views += total_views
            wiki_data["total_weekly_views"] = total_views
        except Exception as e:
            print(f"Error fetching Wiki for {clean_show_name}: {e}")
            wiki_data = {"points": [], "total_weekly_views": 0}
            total_views = 0

        collected_data.append({
            "clean_name": clean_show_name,
            "kalshi_score": kalshi_score,
            "kalshi_data": market,
            "yt_score": yt_score,
            "yt_data": yt_data,
            "news_score": news_score,
            "news_data": news_data,
            "tmdb_score": tmdb_score,
            "tmdb_data": tmdb_data,
            "wiki_views": total_views,
            "wiki_data": wiki_data
        })

    # --- Phase 2: Calculate Final Scores ---
    analyzed_shows = []
    
    for item in collected_data:
        wiki_score = 0.0
        if grand_total_wiki_views > 0:
            wiki_score = (item["wiki_views"] / grand_total_wiki_views) * 100
            
        weighted_score = (
            (item["kalshi_score"] * 0.50) +
            (item["yt_score"] * 0.20) +
            (item["news_score"] * 0.15) +
            (item["tmdb_score"] * 0.10) +
            (wiki_score * 0.05)
        )
        
        item["wiki_data"]["score"] = round(wiki_score, 1)
        
        show_obj = {
            "show_name": item["clean_name"],
            "final_composite_score": round(weighted_score, 1),
            "kalshi": item["kalshi_data"],
            # Structure Matches Request: Includes detailed videos AND totals
            "youtube": {
                "score": item["yt_score"],
                "totals": item["yt_data"].get("totals", {}),
                "videos": item["yt_data"].get("videos", [])
            },
            "news": item["news_data"],
            "tmdb": item["tmdb_data"],
            "wikipedia": item["wiki_data"]
        }
        analyzed_shows.append(show_obj)

    analyzed_shows.sort(key=lambda x: x["final_composite_score"], reverse=True)

    final_payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "shows": analyzed_shows
    }

    _save_snapshot(final_payload)
    return final_payload