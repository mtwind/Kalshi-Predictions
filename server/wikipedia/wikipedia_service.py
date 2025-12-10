# server/wikipedia/wikipedia_service.py
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import requests
from fastapi import HTTPException

DATA_DIR = Path("data/wikipedia")
DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = (
    "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
    "{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}"
)

# NEW: load user agent from env, or fall back to a default
WIKIPEDIA_USER_AGENT = os.getenv(
    "WIKIPEDIA_USER_AGENT",
    "KalshiAltData/0.1 (contact: mtwindpurdue@gmail.com)",
)


def _slugify(value: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-")


def _save_payload(prefix: str, payload: dict) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}-{ts}.json"
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)


def _date_iso_to_yyyymmdd(d: str) -> str:
    dt = datetime.strptime(d, "%Y-%m-%d")
    return dt.strftime("%Y%m%d")


def get_pageviews_daily(
    article_title: str,
    start_date: str,
    end_date: str,
    project: str = "en.wikipedia",
    access: str = "all-access",
    agent: str = "all-agents",
    granularity: str = "daily",
) -> Dict:
    start = _date_iso_to_yyyymmdd(start_date)
    end = _date_iso_to_yyyymmdd(end_date)

    url = BASE_URL.format(
        project=project,
        access=access,
        agent=agent,
        article=article_title,
        granularity=granularity,
        start=start,
        end=end,
    )

    headers = {
        "User-Agent": WIKIPEDIA_USER_AGENT,
    }

    r = requests.get(url, headers=headers, timeout=10)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()

    items = data.get("items", [])
    points = [
        {
            "date": item.get("timestamp", "")[:8],
            "views": item.get("views", 0),
        }
        for item in items
    ]

    payload: Dict = {
        "article_title": article_title,
        "project": project,
        "access": access,
        "agent": agent,
        "granularity": granularity,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(points),
        "points": points,
        "raw": data,
    }

    _save_payload(f"pageviews-{_slugify(article_title)}", payload)
    return payload
