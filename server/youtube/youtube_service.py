# server/youtube/youtube_service.py
from __future__ import annotations

import json
import os
import time
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

# ... (Keep existing search_videos, get_video_stats, etc. as they were) ...
# For brevity, I am appending the NEW logic below. Ensure previous functions exist.

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

def get_video_comments_simple(video_id: str, max_results: int = 10) -> List[Dict]:
    """Helper to fetch raw text comments for analysis."""
    params = {
        "key": API_KEY,
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_results,
        "textFormat": "plainText",
    }
    try:
        r = requests.get(YOUTUBE_COMMENT_THREADS_URL, params=params, timeout=5)
        if not r.ok: return []
        data = r.json()
        comments = []
        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": top["textDisplay"],
                "likes": top["likeCount"]
            })
        return comments
    except Exception:
        return []

# ---------- NEW: Deep Analysis Function ----------

def get_show_analysis(show_name: str) -> Dict:
    """
    Orchestrates a deep dive analysis:
    1. Top 10 general videos -> Avg Stats
    2. Official Trailer -> Specific Stats
    3. Comments -> Sentiment Analysis
    """
    
    # 1. Search for General Videos (Top 10)
    search_res = search_videos(query=show_name, max_results=10)
    video_ids = [v["video_id"] for v in search_res["videos"]]
    
    # 2. Get Stats for General Videos
    stats_res = get_video_stats(video_ids)
    general_videos = stats_res["videos"]
    
    avg_views = 0
    avg_likes = 0
    if general_videos:
        avg_views = sum(v["view_count"] for v in general_videos) // len(general_videos)
        avg_likes = sum(v["like_count"] for v in general_videos) // len(general_videos)

    # 3. Find Official Trailer (Top 1 specific search)
    trailer_search = search_videos(query=f"{show_name} official trailer", max_results=1)
    trailer_data = {}
    if trailer_search["videos"]:
        t_id = trailer_search["videos"][0]["video_id"]
        t_stats = get_video_stats([t_id])
        if t_stats["videos"]:
            trailer_data = t_stats["videos"][0]

    # 4. Sentiment Analysis (10 comments from top 5 videos = 50 comments max to save quota)
    # Note: Youtube quota is expensive. We limit to top 5 videos for comments.
    comments_to_analyze = []
    videos_for_comments = video_ids[:5] 
    
    for vid in videos_for_comments:
        comments = get_video_comments_simple(vid, max_results=10)
        comments_to_analyze.extend(comments)
        
    avg_sentiment = 0.0
    if comments_to_analyze:
        total_score = 0.0
        total_weight = 0.0
        
        for c in comments_to_analyze:
            # Analyze text
            score = _analyzer.polarity_scores(c["text"])["compound"]
            
            # Weight by likes (comments with more likes matter more)
            # Add 1 to weight to avoid zero multiplication
            weight = c["likes"] + 1 
            
            total_score += score * weight
            total_weight += weight
            
        if total_weight > 0:
            avg_sentiment = total_score / total_weight

    payload = {
        "show_name": show_name,
        "avg_video_views": avg_views,
        "avg_video_likes": avg_likes,
        "trailer_views": trailer_data.get("view_count", 0),
        "trailer_likes": trailer_data.get("like_count", 0),
        "sentiment_score": round(avg_sentiment, 4),
        "comment_sample_size": len(comments_to_analyze)
    }
    
    _save_payload(f"analysis-{_slugify(show_name)}", payload)
    return payload