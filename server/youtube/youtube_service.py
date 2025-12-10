# server/youtube/youtube_service.py
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

DATA_DIR = Path("data/youtube")
DATA_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_COMMENT_THREADS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"



def _slugify(value: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-")


def _save_payload(prefix: str, payload: dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}-{ts}.json"
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)


# ---------- 1) Basic search ----------

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
        "type": "video",    # we still ask for only videos
        "q": query,
        "maxResults": max_results,
        "order": order,
    }
    if published_after:
        params["publishedAfter"] = published_after

    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)

    # show YouTube's error instead of a generic 500
    try:
        r.raise_for_status()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()

    videos: List[Dict] = []
    for item in data.get("items", []):
        id_info = item.get("id") or {}
        video_id = id_info.get("videoId")
        if not video_id:
            # skip any weird items that don't have a videoId
            continue

        snippet = item.get("snippet", {})
        videos.append(
            {
                "video_id": video_id,
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
            }
        )

    payload: Dict = {
        "query": query,
        "max_results": max_results,
        "order": order,
        "published_after": published_after,
        "count": len(videos),
        "videos": videos,
        "raw": data,
    }

    _save_payload(f"search-{_slugify(query)}", payload)
    return payload


# ---------- 2) Video stats ----------

def get_video_stats(video_ids: List[str]) -> Dict:
    """
    Fetch statistics (views, likes, comments) for one or more videos.
    """
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY not set in environment")
    if not video_ids:
        return {"videos": []}

    params = {
        "key": API_KEY,
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "maxResults": len(video_ids),
    }

    r = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    videos: List[Dict] = []
    for item in data.get("items", []):
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        videos.append(
            {
                "video_id": item["id"],
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                "comment_count": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
            }
        )

    payload = {"videos": videos, "raw": data}
    _save_payload("stats-" + "_".join(video_ids), payload)
    return payload


# ---------- 3) Convenience: trailer metrics for a show ----------

def get_trailer_metrics(show_name: str, max_results: int = 5) -> Dict:
    """
    Convenience helper:
    - searches for "<show_name> official trailer"
    - gets the top N videos
    - fetches statistics for those videos
    """
    query = f"{show_name} official trailer"
    search_result = search_videos(query=query, max_results=max_results, order="relevance")

    video_ids = [v["video_id"] for v in search_result["videos"]]
    stats_result = get_video_stats(video_ids)

    payload = {
        "show_name": show_name,
        "query": query,
        "search": search_result,
        "stats": stats_result,
    }

    _save_payload(f"trailer-metrics-{_slugify(show_name)}", payload)
    return payload

# ---------- 4) Video Comments ----------

def get_video_comments(
    video_id: str,
    max_results: int = 50,
    order: str = "relevance",  # "relevance" or "time"
) -> Dict:
    """
    Fetch top-level comments for a given video.
    NOTE: Uses YouTube Data API's commentThreads.list endpoint.
    """
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY not set in environment")

    params = {
        "key": API_KEY,
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_results,
        "order": order,
        "textFormat": "plainText",
    }

    r = requests.get(YOUTUBE_COMMENT_THREADS_URL, params=params, timeout=10)

    # If YouTube returns 4xx/5xx (comments disabled, quota, etc.), surface it directly
    if not r.ok:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()

    comments: List[Dict] = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {}) or {}
        top_comment = (snippet.get("topLevelComment") or {}).get("snippet", {}) or {}
        comments.append(
            {
                "author_display_name": top_comment.get("authorDisplayName"),
                "author_channel_id": (top_comment.get("authorChannelId") or {}).get(
                    "value"
                ),
                "text": top_comment.get("textDisplay"),
                "like_count": top_comment.get("likeCount"),
                "published_at": top_comment.get("publishedAt"),
                "updated_at": top_comment.get("updatedAt"),
            }
        )

    payload: Dict = {
        "video_id": video_id,
        "max_results": max_results,
        "order": order,
        "count": len(comments),
        "comments": comments,
        "raw": data,
    }

    _save_payload(f"comments-{_slugify(video_id)}", payload)
    return payload

# ---------- 5) Related videos ----------

def get_related_videos(
    video_id: str,
    max_results: int = 10,
) -> Dict:
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY not set in environment")

    params = {
        "key": API_KEY,
        "part": "snippet",
        "type": "video",
        "relatedToVideoId": video_id,
        "maxResults": max_results,
    }

    r = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
    if not r.ok:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()

    videos: List[Dict] = []
    for item in data.get("items", []):
        id_info = item.get("id") or {}
        related_video_id = id_info.get("videoId")
        if not related_video_id:
            continue

        snippet = item.get("snippet", {}) or {}
        videos.append(
            {
                "video_id": related_video_id,
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
            }
        )

    payload: Dict = {
        "video_id": video_id,
        "max_results": max_results,
        "count": len(videos),
        "videos": videos,
        "raw": data,
    }

    _save_payload(f"related-{_slugify(video_id)}", payload)
    return payload
