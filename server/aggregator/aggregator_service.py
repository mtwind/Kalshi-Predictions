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

# --- DEFAULT MODELS ---
DEFAULT_YOUTUBE_DATA = {
    "totals": {
        "total_views": 0, "total_likes": 0, "average_views": 0,
        "average_likes": 0, "like_percentage": 0, "sentiment_average": 0, "youtube_score": 0
    },
    "videos": []
}
DEFAULT_NEWS_DATA = {"news_score": 0, "article_count": 0, "sentiment_score": 0, "top_articles": []}
DEFAULT_TMDB_DATA = {"tmdb_score": 0, "vote_average": 0, "popularity": 0}
DEFAULT_WIKI_DATA = {"points": [], "avg_daily_views": 0, "total_weekly_views": 0}


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


# ---------- NEW: Pure Logic Function ----------

def apply_scoring_logic(shows_data: List[Dict]) -> List[Dict]:
    """
    Takes a list of shows with RAW data (kalshi, youtube, etc.) and:
    1. Calculates relative metrics (e.g. Wiki share).
    2. Computes weighted Composite Score.
    3. Normalizes scores to 100% probability (Fair Price).
    4. Determines Buy/Sell/Hold edge.
    """
    processed_shows = []
    
    # 1. First Pass: Gather Totals for Relative Scoring
    grand_total_wiki_views = sum(
        s.get("wikipedia", {}).get("total_weekly_views", 0) for s in shows_data
    )
    
    total_composite_score_sum = 0.0
    temp_scored_shows = []

    # 2. Second Pass: Calculate Individual Scores
    for show in shows_data:
        # Extract Raw Metrics
        # Safety checks using defaults in case of malformed data
        k_data = show.get("kalshi", {})
        y_data = show.get("youtube", {})
        n_data = show.get("news", {})
        t_data = show.get("tmdb", {})
        w_data = show.get("wikipedia", {})

        # 1. Kalshi (50%)
        # Priority: Last Price -> Bid -> 0
        kalshi_val = k_data.get("last_price") or k_data.get("yes_bid") or 0
        kalshi_score = float(kalshi_val)

        # 2. YouTube (20%)
        # Structure check: might be in 'totals' or direct (legacy safety)
        if "totals" in y_data:
            yt_score = float(y_data["totals"].get("youtube_score", 0))
        else:
            yt_score = 0.0

        # 3. News (15%)
        news_score = float(n_data.get("news_score", 0))

        # 4. TMDB (10%)
        tmdb_score = float(t_data.get("tmdb_score", 0))

        # 5. Wikipedia (5%) - Relative
        wiki_views = w_data.get("total_weekly_views", 0)
        wiki_score = 0.0
        if grand_total_wiki_views > 0:
            wiki_score = (wiki_views / grand_total_wiki_views) * 100
        
        # Save calculated Wiki score back to object for display
        w_data["score"] = round(wiki_score, 1)

        # --- WEIGHTED FORMULA ---
        weighted_score = (
            (kalshi_score * 0.50) +
            (yt_score * 0.20) +
            (news_score * 0.15) +
            (tmdb_score * 0.10) +
            (wiki_score * 0.05)
        )
        
        total_composite_score_sum += weighted_score
        
        # Store temp data
        temp_scored_shows.append({
            "data": show,
            "raw_score": weighted_score
        })

    # 3. Third Pass: Normalization & Edge Calculation
    for item in temp_scored_shows:
        show = item["data"]
        raw_score = item["raw_score"]
        
        # A. Calculate Fair Price (Probability)
        # Normalization: (My Score / Total Score Pie) * 100
        fair_price = 0.0
        if total_composite_score_sum > 0:
            fair_price = (raw_score / total_composite_score_sum) * 100
            
        fair_price = round(fair_price, 1)
        
        # B. Determine Edge
        market = show.get("kalshi", {})
        market_ask = market.get("yes_ask", 100) # Cost to Buy Yes
        market_bid = market.get("yes_bid", 0)   # Profit to Sell Yes
        
        recommendation = "HOLD"
        edge_value = 0.0
        MARGIN = 5.0  # Conservative margin required to trade
        
        # Buy Signal: My Fair Price is significantly higher than market asking price
        if fair_price > (market_ask + MARGIN):
            recommendation = "BUY YES"
            edge_value = round(fair_price - market_ask, 1)
            
        # Sell Signal: My Fair Price is significantly lower than what I can sell it for
        elif fair_price < (market_bid - MARGIN):
            recommendation = "SELL YES"
            edge_value = round(market_bid - fair_price, 1)

        # Construct Final Object
        processed_shows.append({
            "show_name": show.get("show_name") or show.get("clean_name"),
            "final_composite_score": round(raw_score, 1),
            "fair_price": fair_price,
            "recommendation": recommendation,
            "edge_points": edge_value,
            
            # Embed Sources
            "kalshi": show.get("kalshi"),
            "youtube": show.get("youtube"),
            "news": show.get("news"),
            "tmdb": show.get("tmdb"),
            "wikipedia": show.get("wikipedia")
        })

    # Sort by Fair Price (Probability) descending
    processed_shows.sort(key=lambda x: x["fair_price"], reverse=True)
    return processed_shows


# ---------- Orchestration Functions ----------

def recalculate_scores() -> Dict:
    """
    Loads the latest snapshot, re-runs the scoring algorithm, and saves a new snapshot.
    Does NOT call any external APIs.
    """
    latest = get_latest_snapshot()
    if not latest or "shows" not in latest:
        return {"error": "No existing analysis found. Please run a full refresh first."}
    
    print("Recalculating scores based on cached data...")
    
    # Extract just the raw source data (ignoring previous scores)
    shows_data = latest["shows"]
    
    # Apply Logic
    new_shows_list = apply_scoring_logic(shows_data)
    
    final_payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "shows": new_shows_list
    }
    
    _save_snapshot(final_payload)
    return final_payload


def run_full_analysis() -> Dict:
    """
    Fetches fresh data from all APIs, then applies scoring logic.
    """
    print("Starting full analysis fetch...")

    # 1. Get Base Data (Kalshi)
    try:
        all_markets = get_event_markets(NETFLIX_EVENT_TICKER)
        markets_sorted = sorted(all_markets, key=_market_sort_key, reverse=True)
        top_markets = markets_sorted[:5]
    except Exception as e:
        print(f"CRITICAL: Failed to fetch Kalshi markets: {e}")
        return {"error": "Failed to fetch base market data", "shows": []}
    
    shows_payload = []
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    date_fmt = "%Y-%m-%d"

    # 2. Fetch External Data
    for market in top_markets:
        raw_show_name = market.get("subtitle")
        if not raw_show_name: continue
            
        clean_show_name = normalize_show_name(raw_show_name)
        print(f"Fetching data for: {clean_show_name}")

        # YouTube
        try:
            yt_data = get_show_analysis(clean_show_name)
            if "totals" not in yt_data: yt_data = DEFAULT_YOUTUBE_DATA
        except Exception:
            yt_data = DEFAULT_YOUTUBE_DATA

        # News
        try:
            news_data = get_news_analysis(clean_show_name)
            if "news_score" not in news_data: news_data = DEFAULT_NEWS_DATA
        except Exception:
            news_data = DEFAULT_NEWS_DATA

        # TMDB
        try:
            tmdb_data = get_tmdb_analysis(clean_show_name)
            if "tmdb_score" not in tmdb_data: tmdb_data = DEFAULT_TMDB_DATA
        except Exception:
            tmdb_data = DEFAULT_TMDB_DATA

        # Wikipedia
        wiki_article_title = clean_show_name.replace(" ", "_")
        try:
            wiki_data = get_pageviews_daily(
                article_title=wiki_article_title, 
                start_date=start_date.strftime(date_fmt),
                end_date=end_date.strftime(date_fmt)
            )
            points = wiki_data.get("points", [])
            total_views = sum(p["views"] for p in points)
            wiki_data["total_weekly_views"] = total_views
            wiki_data["avg_daily_views"] = total_views // len(points) if points else 0
        except Exception:
            wiki_data = DEFAULT_WIKI_DATA

        # Build Raw Object
        shows_payload.append({
            "show_name": clean_show_name,
            "kalshi": market,
            "youtube": yt_data,
            "news": news_data,
            "tmdb": tmdb_data,
            "wikipedia": wiki_data
        })

    # 3. Apply Scoring Logic
    final_shows = apply_scoring_logic(shows_payload)

    final_payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "shows": final_shows
    }

    _save_snapshot(final_payload)
    return final_payload