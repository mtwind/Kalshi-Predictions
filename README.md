## Purpose

This application is designed to gather data from various alternative data sources and use these to make informed predictions on specific Kalshi Markets.

For now, there are three primary markets that we are looking to analyze:

1. [Weather markets in Austin, Texas](https://kalshi.com/markets/kxhighaus/highest-temperature-in-austin/kxhighaus-25dec08)
2. [Billboard Top 200 Charts](https://kalshi.com/markets/kxtopalbum/billboard-top-200-1/kxtopalbum-25dec20)
3. [Top US Netflix Show](https://kalshi.com/markets/kxnetflixrankshow/netflix-tv-ranking/kxnetflixrankshow-25dec08)

## Top Netflix Show

[Top US Netflix show this week? | Trade on Kalshi](https://kalshi.com/markets/kxnetflixrankshow/netflix-tv-ranking/kxnetflixrankshow-25dec08)

### How is the Top Show Determined?

- On the home page of Netflix, there is a section labeled Top 10 TV Shows in the U.S. Today
- This is where the ranking updates: [Top 10 Shows on Netflix Right Now](https://www.netflix.com/tudum/top10/tv)
  - Netflix ranking methodology:
    - Hours viewed determines outcomes
    - Not account count
- Contract resolves at 10:00 AM ET following the weekly Netflix top 10 chart update
  - Typically updates Tuesdays around 10 AM ET
- What if Netflix corrects its chart later
  - Kalshi still settles on the first published version

### What Data Sources Can We Use to Build Predictions?

#### Popularity/Streaming Indicators:

1. Netflix Tudum Top 10: [Netflix Tudum - Go behind the streams](https://www.netflix.com/tudum)
2. FlixPatrol: [TOP 10 on Streaming in the World • FlixPatrol](https://flixpatrol.com/)

#### Social Sentiment & Engagement

1. X API or scrapers for real-time mentions, sentiment
2. TikTok API / Hashtag analytics
3. Reddit forums for discussion

#### Search Trends

1. Google trends for shows by name
2. YouTube Analytics for to see how trailers perform
3. Wikipedia pageviews

## To Run

**Server**

```
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
[Swagger Docs](http://localhost:8000/docs)
```

**Client**

```
npm install
npm run dev
```

## API Documentation

| API                        | Required Format           | Example                   |
| -------------------------- | ------------------------- | ------------------------- |
| **Google Trends**          | `"YYYY-MM-DD YYYY-MM-DD"` | `"2025-12-02 2025-12-09"` |
| **Wikipedia Pageviews**    | `YYYYMMDD`                | `20251202`                |
| **TMDB**                   | `YYYY-MM-DD`              | `2025-12-02`              |
| **YouTube**                | `YYYY-MM-DDTHH:MM:SSZ`    | `2025-12-09T00:00:00Z`    |
| **Google News** (your API) | `YYYY-MM-DD`              | `2025-12-02`              |
