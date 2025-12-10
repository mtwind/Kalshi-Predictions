# server/app.py
from fastapi import FastAPI

from trends.routes import router as trends_router
from kalshi_market.routes import router as kalshi_router
from youtube.routes import router as youtube_router
from wikipedia.routes import router as wikipedia_router
from tmdb.routes import router as tmdb_router
from google_news.routes import router as google_news_router
from google_news.routes import router as google_news_router
# from reddit.routes import router as reddit_router  # when ready

app = FastAPI(title="Data Aggregation Backend")

app.include_router(trends_router, prefix="/trends", tags=["Google Trends"])
app.include_router(kalshi_router, prefix="/kalshi", tags=["Kalshi Markets"])
app.include_router(youtube_router, prefix="/youtube", tags=["YouTube"])
app.include_router(wikipedia_router, prefix="/wikipedia", tags=["Wikipedia"])
app.include_router(tmdb_router, prefix="/tmdb", tags=["TMDB"])
app.include_router(google_news_router, prefix="/google-news", tags=["Google News"])

