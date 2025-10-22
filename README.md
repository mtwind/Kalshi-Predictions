# Kalshi-Predictions

## Architecture at a glance

- Frontend (Vite + React): purely UI. Calls your API; subscribes to live updates.
- API/Collector (Node): Express (HTTP API) + BullMQ (background jobs) + Redis (queue/cache).
- DB: Postgres for persisted, queryable history; Redis for fast, “latest snapshot” cache.
- Schedulers: BullMQ repeatable jobs (or cron) per source at sensible cadences.
- Realtime: Server-Sent Events (SSE) or WebSocket to push fresh snapshots to the dashboard.

## Recommended fetch cadence (sane defaults)
- Tudum (Netflix official): weekly snapshot Tue ~10:00 ET; one “label” job.
- FlixPatrol: daily (morning) + optional midday.
- X/Twitter: every 30–60 min (respect your tier limits).
- TikTok: hourly (or 3–6h if limits are tight).
- Reddit: hourly.
- Google Trends: daily, plus hourly for watchlist shows during Fri–Sun.
- YouTube (trailer stats): daily.
- Wikipedia pageviews: hourly.