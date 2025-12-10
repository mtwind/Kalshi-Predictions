# server/google_news/news_service.py
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from fastapi import HTTPException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DATA_DIR = Path("data/google_news")
DATA_DIR.mkdir(parents=True, exist_ok=True)

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GNEWS_BASE_URL = "https://gnews.io/api/v4"

_analyzer = SentimentIntensityAnalyzer()

def _require_api_key() -> str:
    if not GNEWS_API_KEY:
        raise RuntimeError("GNEWS_API_KEY not set in environment")
    return GNEWS_API_KEY


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


def _clean_query(text: str) -> str:
    """
    Remove special characters that cause syntax errors in GNews (like colons).
    Replaces them with a space.
    Example: "Sean Combs: The Reckoning" -> "Sean Combs  The Reckoning"
    """
    # Keep alphanumeric, spaces, hyphens, and apostrophes. 
    # Remove everything else (including colons, parens, quotes).
    return re.sub(r"[^a-zA-Z0-9\s\-\']", "", text).strip()


def search_news(
    query: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    language: str = "en",
    max_results: int = 20,
    sort_by: str = "publishedAt",
) -> Dict:
    api_key = _require_api_key()

    params = {
        "q": query,
        "apikey": api_key,
        "lang": language,
        "max": max_results,
        "sortby": sort_by,
    }
    if from_date:
        params["from"] = f"{from_date}T00:00:00Z"
    if to_date:
        params["to"] = f"{to_date}T23:59:59Z"

    r = requests.get(f"{GNEWS_BASE_URL}/search", params=params, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        # Pass the upstream error detail so we know why it failed
        raise HTTPException(status_code=r.status_code, detail=f"GNews API Error: {r.text}")

    data = r.json()
    articles = []
    
    for a in data.get("articles", []):
        source = a.get("source") or {}
        title = a.get("title") or ""
        desc = a.get("description") or ""
        content = a.get("content") or ""
        
        # Combine text for better sentiment context
        text_to_analyze = f"{title}. {desc}. {content}"
        
        sentiment_score = _analyzer.polarity_scores(text_to_analyze)["compound"]

        articles.append(
            {
                "title": title,
                "description": desc,
                "url": a.get("url"),
                "image": a.get("image"),
                "published_at": a.get("publishedAt"),
                "source_name": source.get("name"),
                "sentiment_score": sentiment_score
            }
        )

    avg_sentiment = 0.0
    if articles:
        avg_sentiment = sum(a["sentiment_score"] for a in articles) / len(articles)

    payload = {
        "query": query,
        "count": data.get("totalArticles", len(articles)),
        "articles": articles,
        "avg_sentiment": avg_sentiment,
    }

    _save_payload(f"news-{_slugify(query)}", payload)
    return payload


def get_news_analysis(show_name: str) -> Dict:
    """
    Orchestrates a news analysis to generate a 'News Score'.
    """
    
    # FIX: Clean the show name to remove colons/syntax errors
    safe_query = _clean_query(show_name)
    print(f"safe_query: {safe_query}, show_name: {show_name}")
    
    # 1. Search recent news using the safe query
    news_data = search_news(query=safe_query, max_results=20, sort_by="publishedAt")
    articles = news_data.get("articles", [])
    count = len(articles)
    avg_sentiment = news_data.get("avg_sentiment", 0.0)
    
    # 2. Calculate Score
    # Sentiment (-1 to 1) -> normalized 0-60 points
    sentiment_points = ((avg_sentiment + 1) / 2) * 60
    
    # Volume -> 0-40 points
    volume_points = (min(count, 20) / 20) * 40
    
    final_score = round(sentiment_points + volume_points, 1)
    
    payload = {
        "show_name": show_name, # Return original name for UI consistency
        "news_score": final_score,
        "sentiment_score": round(avg_sentiment, 2),
        "article_count": count,
        "top_articles": articles[:2] 
    }
    
    _save_payload(f"analysis-{_slugify(show_name)}", payload)
    return payload