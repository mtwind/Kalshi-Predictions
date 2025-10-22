# Kalshi-Predictions

## Architecture at a glance

- **Frontend (Vite + React)**: purely UI. Calls your API; subscribes to live updates.
- **API/Collector (Node)**: Express (HTTP API) + BullMQ (background jobs) + Redis (queue/cache).
- **DB**: Postgres for persisted, queryable history; Redis for fast, “latest snapshot” cache.
- **Schedulers**: BullMQ repeatable jobs (or cron) per source at sensible cadences.
- **Realtime**: Server-Sent Events (SSE) or WebSocket to push fresh snapshots to the dashboard.

---

## Recommended fetch cadence (sane defaults)

- **Tudum (Netflix official)**: weekly snapshot **Tue ~10:00 ET**; one “label” job.
- **FlixPatrol**: **daily** (morning) + optional **midday**.
- **X/Twitter**: **every 30–60 min** (respect your tier limits).
- **TikTok**: **hourly** (or 3–6h if limits are tight).
- **Reddit**: **hourly**.
- **Google Trends**: **daily**, plus **hourly** for watchlist shows during Fri–Sun.
- **YouTube** (trailer stats): **daily**.
- **Wikipedia pageviews**: **hourly**.

## Folder layout (server)

```bash
server/
  src/
    index.ts                 # express bootstrap
    routes/
      sources.ts             # /api/sources (list, status)
      shows.ts               # /api/shows/:id/metrics (latest window)
      stream.ts              # /api/stream (SSE)
    jobs/
      schedule.ts            # register recurring jobs
      runners/
        netflix.tudum.ts
        flixpatrol.ts
        x.twitter.ts
        tiktok.ts
        reddit.ts
        google.trends.ts
        youtube.ts
        wikipedia.ts
    lib/
      bullmq.ts              # queue + connection
      db.ts                  # postgres client (knex/prisma)
      redis.ts               # redis client
      logger.ts
      normalizers.ts         # map raw -> common schema
    models/
      upserts.ts             # insert/update helpers
    config/
      env.ts
  package.json

```

## # Data flow

1. **Scheduler** enqueues repeatable jobs per source (BullMQ `repeat`).
2. **Runner** hits the third-party API, normalizes the response, and:
    - writes **raw** → `raw_events_*` (optional, useful for debugging),
    - writes **normalized snapshot** → Postgres (`source_snapshots`),
    - updates Redis key `source:<key>:latest` with a compact JSON snapshot.
3. **API** serves:
    - `GET /api/sources` → list of sources + lastUpdated + health
    - `GET /api/shows/:id/metrics?window=7d` → merged time-series for charts
    - `GET /api/stream` (SSE) → pushes `{source, ts, payload}` when new data lands
4. **Frontend**:
    - On load, fetch `/api/sources` for card state.
    - Open SSE to update cards in real time.
    - When user opens a details panel, fetch `/api/shows/:id/metrics`.