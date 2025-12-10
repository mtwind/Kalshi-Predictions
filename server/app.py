from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from trends.routes import router as trends_router
from kalshi_market.routes import router as kalshi_router
from youtube.routes import router as youtube_router
from wikipedia.routes import router as wikipedia_router
from tmdb.routes import router as tmdb_router
from google_news.routes import router as google_news_router
from aggregator.routes import router as aggregator_router

app = FastAPI(title="Data Aggregation Backend")

# ------------------------------------------------------------
# CORS Configuration (Fixes the frontend access error)
# ------------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
app.include_router(trends_router, prefix="/trends", tags=["Google Trends"])
app.include_router(kalshi_router, prefix="/kalshi", tags=["Kalshi Markets"])
app.include_router(youtube_router, prefix="/youtube", tags=["YouTube"])
app.include_router(wikipedia_router, prefix="/wikipedia", tags=["Wikipedia"])
app.include_router(tmdb_router, prefix="/tmdb", tags=["TMDB"])
app.include_router(google_news_router, prefix="/google-news", tags=["Google News"])

# Register the Aggregator
app.include_router(aggregator_router, prefix="/aggregator", tags=["Aggregator"])

@app.get("/")
def root():
    return {"message": "Kalshi Alternative Data API is running"}