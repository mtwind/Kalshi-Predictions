# trends_service.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Literal

from pytrends.request import TrendReq
from .categories import category_to_id


# Directory where JSON outputs will be stored
DATA_DIR = Path("data/trends")
DATA_DIR.mkdir(exist_ok=True)

# Shared pytrends client
pytrends = TrendReq(hl="en-US", tz=-300)  # US-ish timezone (UTC-5)


# ---------- Utility helpers ----------

def slugify(value: str) -> str:
    """Convert a string into a simple URL/file-system friendly slug."""
    return "".join(
        c.lower() if c.isalnum() else "-"
        for c in value
    ).strip("-")


def save_to_json(payload: dict, filename: str) -> str:
    """
    Save payload into data/<filename> as pretty JSON.
    Returns the file path as string.
    """
    path = DATA_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(path)


# ---------- 1) Single-term interest over time ----------

def fetch_interest_single(
    search_term: str,
    start_date: str,
    end_date: str,
    geo: str = "US",
    category: str = "All",
) -> Dict:
    """
    Fetch interest over time for a single search term.

    - search_term: keyword to query
    - start_date, end_date: 'YYYY-MM-DD' strings
    - geo: Google Trends geo code (e.g. 'US', 'GB', '')
    - category: human-readable category string mapped via category_to_id(...)
    """
    cat_id = category_to_id(category)
    timeframe = f"{start_date} {end_date}"

    pytrends.build_payload(
        kw_list=[search_term],
        timeframe=timeframe,
        geo=geo,
        cat=cat_id,
    )

    df = pytrends.interest_over_time()

    if df.empty:
        points: List[Dict] = []
    else:
        df = df.reset_index()
        points = [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "value": int(row[search_term]),
            }
            for _, row in df.iterrows()
        ]

    payload: Dict = {
        "search_term": search_term,
        "start_date": start_date,
        "end_date": end_date,
        "geo": geo,
        "category": category,
        "category_id": cat_id,
        "points": points,
    }

    filename = f"single-{slugify(search_term)}-{start_date}_{end_date}-cat{cat_id}.json"
    save_to_json(payload, filename)

    return payload


# ---------- 2) Multi-term compare interest over time ----------

def fetch_interest_compare(
    search_terms: List[str],
    start_date: str,
    end_date: str,
    geo: str = "US",
    category: str = "All",
) -> Dict:
    """
    Use Google Trends compare feature for multiple terms.

    - search_terms: list of keywords
    - returns 'series': { term -> [ { date, value }, ... ] }
    """
    cat_id = category_to_id(category)
    timeframe = f"{start_date} {end_date}"

    if not search_terms:
        return {
            "search_terms": [],
            "start_date": start_date,
            "end_date": end_date,
            "geo": geo,
            "category": category,
            "category_id": cat_id,
            "series": {},
        }

    pytrends.build_payload(
        kw_list=search_terms,
        timeframe=timeframe,
        geo=geo,
        cat=cat_id,
    )

    df = pytrends.interest_over_time()

    if df.empty:
        series: Dict[str, List[Dict]] = {term: [] for term in search_terms}
    else:
        df = df.reset_index()
        series = {}
        for term in search_terms:
            if term not in df.columns:
                series[term] = []
                continue
            series[term] = [
                {
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "value": int(row[term]),
                }
                for _, row in df.iterrows()
            ]

    payload: Dict = {
        "search_terms": search_terms,
        "start_date": start_date,
        "end_date": end_date,
        "geo": geo,
        "category": category,
        "category_id": cat_id,
        "series": series,
    }

    joined = "_vs_".join(slugify(t) for t in search_terms)
    filename = f"compare-{joined}-{start_date}_{end_date}-cat{cat_id}.json"
    save_to_json(payload, filename)

    return payload


# ---------- 3) Related topics / related queries ----------

def fetch_related(
    search_term: str,
    geo: str = "US",
    category: str = "All",
    timeframe: str = "today 12-m",
    mode: Literal["topics", "queries"] = "queries",
) -> Dict:
    """
    Fetch related topics or related queries for a search term.

    - mode="topics": uses pytrends.related_topics()
    - mode="queries": uses pytrends.related_queries()
    - timeframe examples: 'today 12-m', 'today 3-m', 'now 7-d', '2023-01-01 2024-01-01'
    """
    cat_id = category_to_id(category)

    pytrends.build_payload(
        kw_list=[search_term],
        timeframe=timeframe,
        geo=geo,
        cat=cat_id,
    )

    def df_to_list(df):
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")

    if mode == "topics":
        topics = pytrends.related_topics()
        entry = topics.get(search_term, {})
        top_df = entry.get("top")
        rising_df = entry.get("rising")

        result: Dict = {
            "search_term": search_term,
            "geo": geo,
            "category": category,
            "category_id": cat_id,
            "timeframe": timeframe,
            "mode": "topics",
            "top": df_to_list(top_df),
            "rising": df_to_list(rising_df),
        }

        filename = (
            f"related-topics-{slugify(search_term)}-{slugify(timeframe)}-cat{cat_id}.json"
        )

    else:  # mode == "queries"
        queries = pytrends.related_queries()
        entry = queries.get(search_term, {})
        top_df = entry.get("top")
        rising_df = entry.get("rising")

        result = {
            "search_term": search_term,
            "geo": geo,
            "category": category,
            "category_id": cat_id,
            "timeframe": timeframe,
            "mode": "queries",
            "top": df_to_list(top_df),
            "rising": df_to_list(rising_df),
        }

        filename = (
            f"related-queries-{slugify(search_term)}-{slugify(timeframe)}-cat{cat_id}.json"
        )

    save_to_json(result, filename)
    return result
