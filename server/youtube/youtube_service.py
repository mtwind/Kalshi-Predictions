# server/youtube/youtube_service.py
from __future__ import annotations

import json
import os
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from fastapi import HTTPException
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
DATA_DIR = Path("data/youtube")
DATA_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_COMMENT_THREADS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

_analyzer = SentimentIntensityAnalyzer()


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


# ---------- 1) Search ----------

def search_videos(
    query: str,
    max_results: int = 10,
    order: str = "relevance",
    published_after: Optional[str] = None,
) -> Dict:
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY not set in environment")

    params = {
        "key": API_KEY,
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": max_results,
        "order": order,
    }
    if published_after:
        params["publishedAfter"] = published_after

    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()
    videos = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            videos.append({
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "channel_title": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
            })

    return {"videos": videos, "raw": data}


# ---------- 2) Video Stats ----------

def get_video_stats(video_ids: List[str]) -> Dict:
    if not API_KEY or not video_ids:
        return {"videos": []}

    params = {
        "key": API_KEY,
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
    }
    r = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    videos = []
    for item in data.get("items", []):
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        
        videos.append({
            "video_id": item["id"],
            "title": snippet.get("title"),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)) if "likeCount" in stats else 0,
            "comment_count": int(stats.get("commentCount", 0)) if "commentCount" in stats else 0,
        })
    return {"videos": videos}


# ---------- 3) Comments & Sentiment Helper ----------

def get_video_sentiment(video_id: str, max_results: int = 50) -> float:
    """
    Fetches top comments for a specific video and returns a weighted sentiment score (-1 to 1).
    """
    if not API_KEY:
        return 0.0

    params = {
        "key": API_KEY,
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_results,
        "textFormat": "plainText",
        "order": "relevance"
    }
    
    try:
        r = requests.get(YOUTUBE_COMMENT_THREADS_URL, params=params, timeout=5)
        if not r.ok:
            return 0.0
        
        data = r.json()
        total_score = 0.0
        total_weight = 0.0

        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            text = top["textDisplay"]
            likes = top.get("likeCount", 0)

            # Sentiment analysis
            polarity = _analyzer.polarity_scores(text)["compound"]
            
            # Weight: Comments with more likes have slightly more impact
            # Logarithmic weighting to avoid one viral comment skewing everything
            weight = 1 + math.log(likes + 1)
            
            total_score += polarity * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0
            
        return round(total_score / total_weight, 4)

    except Exception:
        return 0.0


# ---------- 4) NEW: Deep Analysis Function ----------

def get_show_analysis(show_name: str) -> Dict:
    """
    1. Search top 10 videos.
    2. Batch fetch stats.
    3. Calculate sentiment for EACH video.
    4. Aggregate totals and calculate a final YouTube Score.
    """
    
    # 1. Search (Top 10)
    search_res = search_videos(query=show_name, max_results=10)
    video_ids = [v["video_id"] for v in search_res["videos"]]
    
    if not video_ids:
        return {
            "show_name": show_name,
            "videos": [],
            "totals": {
                "total_views": 0,
                "total_likes": 0,
                "average_views": 0,
                "average_likes": 0,
                "like_percentage": 0,
                "sentiment_average": 0,
                "youtube_score": 0
            }
        }

    # 2. Get Stats Batch
    stats_res = get_video_stats(video_ids)
    raw_videos = stats_res["videos"]

    detailed_videos = []
    
    sum_views = 0
    sum_likes = 0
    sum_sentiment = 0.0
    
    # 3. Process Each Video (Stats + Sentiment)
    for vid in raw_videos:
        # Sentiment Analysis (1 API call per video)
        sentiment = get_video_sentiment(vid["video_id"], max_results=50)
        
        detailed_video = {
            "video_id": vid["video_id"],
            "title": vid["title"],
            "view_count": vid["view_count"],
            "like_count": vid["like_count"],
            "comment_count": vid["comment_count"],
            "sentiment_score": sentiment
        }
        detailed_videos.append(detailed_video)
        
        # Accumulate
        sum_views += vid["view_count"]
        sum_likes += vid["like_count"]
        sum_sentiment += sentiment

    count = len(detailed_videos)
    if count == 0:
        count = 1 

    # 4. Calculate Totals
    avg_views = sum_views // count
    avg_likes = sum_likes // count
    avg_sentiment = round(sum_sentiment / count, 4)
    
    # Like Percentage (Total Likes / Total Views)
    like_percentage = 0.0
    if sum_views > 0:
        like_percentage = round((sum_likes / sum_views) * 100, 2)

    # 5. YouTube Score Calculation (0-100)
    # Heuristic: 
    # - Popularity: Log scale of Avg Views. 100k avg = ~50pts. 10M avg = ~90pts.
    # - Sentiment: Boosts score by up to 20 points.
    
    # Base score from views (Max ~80)
    # log10(1,000,000) = 6. log10(100,000) = 5.
    # We want 1M avg views to be a strong score (e.g. 60)
    views_score = min(math.log(avg_views + 1, 10) * 10, 80)
    
    # Sentiment Adjustment (-1.0 to 1.0) -> mapped to (-10 to +20)
    # Good sentiment should boost, bad should penalize slightly
    sentiment_impact = (avg_sentiment * 15) + 5 
    
    youtube_score = round(views_score + sentiment_impact, 1)
    # Cap at 100
    youtube_score = min(max(youtube_score, 0), 100)

    totals = {
        "total_views": sum_views,
        "total_likes": sum_likes,
        "average_views": avg_views,
        "average_likes": avg_likes,
        "like_percentage": like_percentage,
        "sentiment_average": avg_sentiment,
        "youtube_score": youtube_score
    }
    
    payload = {
        "show_name": show_name,
        "videos": detailed_videos,
        "totals": totals
    }
    
    _save_payload(f"analysis-{_slugify(show_name)}", payload)
    return payload

# ... (Keep existing legacy functions: get_trailer_metrics, get_video_comments, get_related_videos) ...
def get_trailer_metrics(show_name: str, max_results: int = 5) -> Dict:
    query = f"{show_name} official trailer"
    search_result = search_videos(query=query, max_results=max_results, order="relevance")
    video_ids = [v["video_id"] for v in search_result["videos"]]
    stats_result = get_video_stats(video_ids)
    payload = {"show_name": show_name, "query": query, "search": search_result, "stats": stats_result}
    _save_payload(f"trailer-metrics-{_slugify(show_name)}", payload)
    return payload

def get_video_comments(video_id: str, max_results: int = 50, order: str = "relevance") -> Dict:
    if not API_KEY: raise RuntimeError("YOUTUBE_API_KEY not set")
    params = {"key": API_KEY, "part": "snippet", "videoId": video_id, "maxResults": max_results, "order": order, "textFormat": "plainText"}
    r = requests.get(YOUTUBE_COMMENT_THREADS_URL, params=params, timeout=10)
    if not r.ok: raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    comments = []
    for item in data.get("items", []):
        top_comment = (item.get("snippet", {}).get("topLevelComment") or {}).get("snippet", {})
        comments.append({
            "author_display_name": top_comment.get("authorDisplayName"),
            "text": top_comment.get("textDisplay"),
            "like_count": top_comment.get("likeCount"),
            "published_at": top_comment.get("publishedAt"),
        })
    return {"comments": comments}

def get_related_videos(video_id: str, max_results: int = 10) -> Dict:
    if not API_KEY: raise RuntimeError("YOUTUBE_API_KEY not set")
    params = {"key": API_KEY, "part": "snippet", "type": "video", "relatedToVideoId": video_id, "maxResults": max_results}
    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
    if not r.ok: raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    videos = []
    for item in data.get("items", []):
        videos.append({"video_id": item.get("id", {}).get("videoId"), "title": item.get("snippet", {}).get("title")})
    return {"videos": videos}