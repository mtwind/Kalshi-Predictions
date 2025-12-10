# # main.py
# from __future__ import annotations

# from typing import List, Literal

# from fastapi import FastAPI
# from pydantic import BaseModel, Field

# from trends_service import (
#     fetch_interest_single,
#     fetch_interest_compare,
#     fetch_related,
# )

# app = FastAPI(title="Google Trends Backend")

# # ---------- Request models ----------

# class InterestSingleRequest(BaseModel):
#     search_term: str = Field(..., description="Keyword to query in Google Trends")
#     start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
#     end_date: str = Field(..., description="End date in YYYY-MM-DD format")
#     geo: str = Field("US", description="Geo code (e.g., 'US', 'GB', '')")
#     category: str = Field(
#         "All",
#         description="Human-readable Google Trends category (e.g. 'Arts & Entertainment/TV & Video')",
#     )

# class InterestCompareRequest(BaseModel):
#     search_terms: List[str] = Field(..., description="List of keywords to compare")
#     start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
#     end_date: str = Field(..., description="End date in YYYY-MM-DD format")
#     geo: str = Field("US", description="Geo code (e.g., 'US', 'GB', '')")
#     category: str = Field(
#         "All",
#         description="Human-readable Google Trends category (e.g. 'Arts & Entertainment/TV & Video')",
#     )

# class RelatedRequest(BaseModel):
#     search_term: str = Field(..., description="Keyword to query")
#     geo: str = Field("US", description="Geo code (e.g., 'US', 'GB', '')")
#     category: str = Field(
#         "All",
#         description="Human-readable Google Trends category (e.g. 'Arts & Entertainment/TV & Video')",
#     )
#     timeframe: str = Field(
#         "today 12-m",
#         description="Google Trends timeframe (e.g. 'today 12-m', 'today 3-m', 'now 7-d')",
#     )
#     mode: Literal["topics", "queries"] = Field(
#         "queries",
#         description="Whether to return related 'topics' or 'queries'",
#     )

# # ---------- Routes ----------

# @app.post("/trends/interest")
# def trends_interest_single(req: InterestSingleRequest):
#     """
#     Single-term interest over time.
#     """
#     payload = fetch_interest_single(
#         search_term=req.search_term,
#         start_date=req.start_date,
#         end_date=req.end_date,
#         geo=req.geo,
#         category=req.category,
#     )
#     return payload


# @app.post("/trends/compare")
# def trends_interest_compare(req: InterestCompareRequest):
#     """
#     Multi-term compare interest over time.
#     """
#     payload = fetch_interest_compare(
#         search_terms=req.search_terms,
#         start_date=req.start_date,
#         end_date=req.end_date,
#         geo=req.geo,
#         category=req.category,
#     )
#     return payload


# @app.post("/trends/related")
# def trends_related(req: RelatedRequest):
#     """
#     Related topics or related queries for a single term.
#     """
#     payload = fetch_related(
#         search_term=req.search_term,
#         geo=req.geo,
#         category=req.category,
#         timeframe=req.timeframe,
#         mode=req.mode,
#     )
#     return payload
