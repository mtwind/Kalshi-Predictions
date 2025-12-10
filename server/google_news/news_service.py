# server/google_news/news_service.py
from __future__ import annotations

import json
import os
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

# Initialize VADER
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


def _get(path: str, params: Dict) -> Dict:
    api_key = _require_api_key()
    url = f"{GNEWS_BASE_URL}{path}"
    params = dict(params)
    params["apikey"] = api_key

    r = requests.get(url, params=params, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()


def search_news(
    query: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    language: str = "en",
    max_results: int = 100, # Increased default to 100
    sort_by: str = "relevance",
) -> Dict:
    """
    Search news articles using GNews.
    Includes robust sentiment analysis using Title + Description + Content.
    """
    params: Dict = {
        "q": query,
        "lang": language,
        "max": max_results,
        "sortby": sort_by,
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    data = _get("/search", params=params)

    articles_raw: List[Dict] = data.get("articles", [])
    articles: List[Dict] = []
    
    for a in articles_raw:
        source = a.get("source") or {}
        title = a.get("title") or ""
        desc = a.get("description") or ""
        content = a.get("content") or ""
        
        # Combine all text for better sentiment context
        text_to_analyze = f"{title}. {desc}. {content}"
        
        # Get sentiment compound score (-1.0 to 1.0)
        sentiment_score = _analyzer.polarity_scores(text_to_analyze)["compound"]

        articles.append(
            {
                "title": title,
                "description": desc,
                "content": content,
                "url": a.get("url"),
                "image": a.get("image"),
                "published_at": a.get("publishedAt"),
                "source_name": source.get("name"),
                "source_url": source.get("url"),
                "sentiment_score": sentiment_score
            }
        )

    # Calculate average sentiment for the search topic
    avg_sentiment = 0.0
    if articles:
        avg_sentiment = sum(a["sentiment_score"] for a in articles) / len(articles)

    payload: Dict = {
        "query": query,
        "from_date": from_date,
        "to_date": to_date,
        "language": language,
        "max_results": max_results,
        "sort_by": sort_by,
        "count": len(articles),
        "average_sentiment": round(avg_sentiment, 4),
        "articles": articles,
        "raw": data,
    }

    _save_payload(f"news-{_slugify(query)}", payload)
    return payload