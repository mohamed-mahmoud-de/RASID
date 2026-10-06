# Architecture

Status: **target design**. Nothing is built yet. Items marked (P-xxx) depend on proposed decisions in `decision-log.md`.

## 1. Data flow

```
                         ┌────────────────────── STREAMING PATH ──────────────────────┐
 aisstream.io ──WSS──▶ collector ──▶ Kafka topic ais.raw ──▶ Spark Structured Streaming
 (live AIS, no SLA)     │ reconnect+backoff                    │ parse · clean · dedupe
                        │ writes raw NDJSON                    │ features/ (shared lib)
                        ▼                                      ├──▶ Silver positions (Parquet)
                 BRONZE (MinIO, immutable)                     └──▶ Feast push ──▶ Redis (online store)
                        ▲
 replay simulator ──────┘ reads Bronze → Kafka at N× speed (tests, demo, drift injection)

                         ┌──────────────────── BATCH PATH (Airflow) ───────────────────┐
                         │ Bronze → Silver backfill · GE quality gates                │
                         │ zone detection (DBSCAN + hull) → zones.geojson (versioned)  │
                         │ episode/label builder → Gold zone-hour tables               │
                         │ features/ (same lib) → Gold features → Feast offline store  │
                         │ weekly: train → evaluate → register challenger              │
                         └─────────────────────────────────────────────────────────────┘

 Feast offline (point-in-time) ──▶ training (XGBoost quantile / LSTM) ──▶ MLflow registry
                                                                        @champion @challenger @previous
 Feast online + MLflow @champion ──▶ FastAPI /v1 ──▶ map dashboard · alerts (email/WhatsApp, later)
 prediction log + matured labels ──▶ monitor (Evidently + perf) ──▶ drift ⇒ retrain | regression ⇒ rollback
```

## 2. Components

| # | Component | Responsibility | Tech | Workstream |
|---|---|---|---|---|
| 1 | Collector | WebSocket subscribe (bbox + message types), reconnect with exponential backoff, write raw NDJSON per hour, publish to Kafka. **Runs 24/7 from day 1, even before Kafka exists** (P-006) | Python `websockets`, `confluent-kafka` | W1 |
| 2 | Kafka | Durable buffer between ingestion and processing. Topics: `ais.raw`, `ais.clean`, `predictions` | Kafka 4.x (KRaft, single broker in dev) | W1 |
| 3 | Stream processor | Parse/clean/dedupe, update vessel state, compute rolling zone features with `features/`, push to Feast | Spark Structured Streaming | W1 |
| 4 | Object storage | Bronze/Silver/Gold Parquet; S3-compatible, so cloud migration is a config change (P-004) | MinIO | W2 |
| 5 | Relational + geo | Zone polygons, vessel registry (static data), episodes, prediction log; spatial queries (P-004) | PostgreSQL + PostGIS | W2 |
| 6 | Orchestrator | Backfills, zone refresh, label build, quality gates, materialization, retraining | Airflow (pin version; v3 API differs from most tutorials) | W2 |
| 7 | Zone & label builder | DBSCAN + hull → zones; episode detection → waiting-time labels | scikit-learn, shapely 2, geopandas | W3 |
| 8 | Feature library `features/` | **Single source of truth for every feature transform.** Pure functions over vessel-state frames, imported by both #3 and #6 (P-001) | Python / PySpark | W4 |
| 9 | Feature store | Entity `zone_id`; offline (Parquet) for point-in-time training sets; online (Redis) for serving; TTL = freshness guard | Feast | W5 |
| 10 | Training | Baselines, XGBoost (quantile), optional LSTM; rolling-origin evaluation; SHAP | xgboost, shap, PyTorch (opt.) | W4 |
| 11 | Registry | Experiments, artifacts, model versions; aliases `@champion` `@challenger` `@previous` (stages are deprecated) (P-008) | MLflow | W5 |
| 12 | Serving | Forecast API; loads `@champion`, hot-reloads on alias change; exposes freshness + model version | FastAPI + uvicorn | W5 |
| 13 | Monitoring | Input drift, freshness, delayed-label performance; triggers retrain/rollback (P-002) | Evidently + custom job + Prometheus | W5 |
| 14 | Dashboard | Map of zones and vessels, forecast bands, drivers; ops panels | Streamlit or React+Leaflet for product; Grafana for ops (P-003) | shared |
| 15 | Replay simulator | Re-stream any Bronze window into Kafka at N× speed; optional fault/drift injection | Python | W1 |

## 3. Medallion layers

| Layer | Content | Format / partitioning | Retention |
|---|---|---|---|
| **Bronze** | Raw aisstream messages exactly as received + `received_at` | NDJSON.gz → compacted daily to Parquet; `date=/hour=` | Forever (it is the moat) |
| **Silver** | `positions` (mmsi, ts, lat, lon, sog, cog, heading, nav_status), cleaned, deduped, sentinel-filtered; `vessels` (static: imo, name, type, length, beam, draught) | Parquet `date=`; PostGIS for `vessels` | Forever |
| **Gold** | `episodes` (mmsi, zone_id, start_ts, end_ts, wait_h, exit_type); `zone_hour` (occupancy, arrivals, departures, median waits, approach pressure, weather); labels per horizon | Parquet + Feast offline source | Forever, versioned by zone set + label version |

## 4. Zones

- Zones are derived, not hand-drawn. DBSCAN (haversine metric) runs on stationary points (SOG < 0.5 kn), then each cluster gets a convex hull, or `shapely.concave_hull` for tighter shapes.
- A cluster is classified as **berth** if it is adjacent to the coastline/quay and mostly NavStatus 5. Otherwise it is **anchorage**.
- **Gate lines** (line segments) mark the canal entrance and port entrance. A vessel crossing a gate line is an unambiguous "service started" event.
- Zones are stored as versioned GeoJSON (`zones/v{N}.geojson`) and loaded into PostGIS. They are **reviewed on a map by a human before use.**
- Changing the zone version invalidates the labels, which must then be rebuilt by Airflow.

## 5. Serving API (draft contract)

```
GET /v1/zones                                   → [{zone_id, name, type, geometry_ref}]
GET /v1/zones/{zone_id}/forecast?horizons=6,12,24
  → {
      "zone_id": "PSD-N-ANCH",
      "issued_at": "2026-12-01T10:00:00Z",
      "model_version": "xgb-q@champion:v7",
      "data_freshness_s": 42,
      "forecasts": [
        {"horizon_h": 6, "occupancy": {"p10": 18, "p50": 23, "p90": 31},
         "expected_wait_h": {"p50": 14.5, "p90": 30.0}, "congestion_level": "HIGH"}
      ],
      "top_drivers": [{"feature": "arrivals_6h", "shap": 3.1}, ...],
      "stale": false
    }
GET /v1/vessels/{mmsi}/status                   → current episode + elapsed wait (phase 3)
GET /healthz · /readyz · /metrics (Prometheus)
```
Rule: if online features are older than their TTL, return `stale: true` and do **not** silently serve a forecast built on old features.

## 6. Repository layout (proposed)

```
rasid/
├── collector/        # aisstream → NDJSON + Kafka
├── replay/           # Bronze → Kafka simulator
├── streaming/        # Spark Structured Streaming jobs
├── features/         # SHARED feature library (only place features are defined)
├── labeling/         # zones (DBSCAN/hull), episodes, labels
├── dags/             # Airflow DAGs
├── feature_repo/     # Feast definitions
├── training/         # baselines, models, evaluation, SHAP
├── serving/          # FastAPI app
├── monitoring/       # drift/perf jobs, rollback controller
├── dashboard/
├── quality/          # Great Expectations suites
├── infra/            # docker-compose.yml (+ profiles), configs, Makefile
├── tests/            # unit + integration (parity test, replay fixtures)
├── claude/           # project docs (this folder)
└── CLAUDE.md
```

## 7. Deployment

- **Dev/demo:** one docker-compose with profiles. Run only what you need.
  - `core`: MinIO, Postgres/PostGIS, Redis
  - `stream`: Kafka, Spark, collector
  - `batch`: Airflow
  - `ml`: MLflow, serving, monitoring
  - `ui`: dashboard, Grafana
- **RAM estimate for the full stack:** ~8–12 GB. Team machines need ≥16 GB, otherwise use profiles.
- **Always-on box:** a small cloud VM runs the collector 24/7 (Azure for Students / GitHub Student Pack credits / Oracle Cloud free tier). The collector must not depend on anyone's laptop.
- **CI (GitHub Actions):** ruff → pytest (unit) → docker build → integration test running a 24 h replay fixture through batch *and* streaming paths → **feature parity assertion**.
