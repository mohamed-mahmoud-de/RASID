# CLAUDE.md — Rasid: Smart Port & Maritime Congestion Predictor

> Persistent project memory for Claude Code sessions. Keep this file short and current; details live in `docs/`.
> Last updated: 2026-10-14

**Working name:** Rasid (راصد — Arabic for "observer"), taken from the project folder name. *Confirm with team.*
**Formal title:** Smart Port & Maritime Congestion Predictor — An AIS-Based Predictive Data Engineering & MLOps Pipeline for Egyptian Maritime Gateways.

## What this is

- **Goal:** forecast near-term vessel congestion (how many ships wait at anchorage, and for how long) **6–12 h ahead** at the Port Said / Suez Canal approaches, so operators plan *before* the queue forms.
- **Problem:** congestion at Egyptian gateways is handled reactively. Waiting at anchorage costs demurrage, detention, fuel, and missed downstream logistics.
- **Two ports, one pipeline (decision D-008):**
  - **Port Said / Suez Canal (main analysis):** trained and backtested on **Global Fishing Watch** satellite AIS (hourly per ship, 2017 → ~5 days ago). Labels are derived from AIS: anchorage occupancy and dwell, following Peng et al. (2023). The data isn't live, so the demo uses the replay simulator.
  - **Alexandria (live showcase):** the **Alexandria Port Authority** public ship board, polled every 30 min (official arrival, berthing and departure times), plus GFW Alexandria history. Live predictions follow a 4–6 week side-by-side overlap.
- **Novel contribution:** AIS-derived congestion forecasting for Egyptian gateways, plus streaming and production MLOps (feature store, registry, drift monitoring, rollback).
- **Two identities:** it is a DE + MLOps graduation project *and* a product candidate. Make decisions that serve both.

## Academic context

- **Alexandria University — Faculty of Science — Software Industry and Multimedia (SIM) Department** (confirmed 2026-10-09; use exactly this wording)
- Supervisor: **Prof. Mohamed Kholief**
- Department requirement: Data Engineering + MLOps project
- Academic year 2026/27. Defense date TBC, roadmap assumes ~June 2027.

## Team (authoritative roster: 5 people, confirmed 2026-10-09)

Use these names, roles and this order in every document.

| Member | Role | Owns |
|---|---|---|
| Mohamed Mahmoud | **Team Lead** — MLOps Engineer & Data Engineer | W5 MLOps & platform; integration; supervisor liaison |
| Reem Adel | Data Engineer | Workstream TBD |
| Alhassan Mohamed | Data Engineer | Workstream TBD |
| Youssef Nasser | Data Engineer | Workstream TBD |
| Youssef Elkomy | Data Engineer | Workstream TBD |

Workstreams W1–W5 are defined in `docs/roadmap.md`. **Gap:** the proposal assigns no one to modeling and evaluation (W4). Assign an owner.

## Data sources (D-008, decided 2026-10-07): free only, no paid data, no hardware

| Source | Port | Role | Notes |
|---|---|---|---|
| Global Fishing Watch, AIS vessel presence | Port Said / Suez + Alexandria | Training, labels, backtests | CC BY-NC 4.0 (non-commercial). ~5-day latency. Validated (Ever Given test). Coarse vessel types |
| Alexandria Port Authority board (`spsonlinealex.apa.gov.eg`) | Alexandria | **Live** source | No API (web extraction, TLS chain completed manually), no history until collected, messy legacy records; written permission requested via the supervisor |
| IMF PortWatch, Suez Canal Authority | Suez / ports | Validation | Daily / monthly counts; the two disagree on trend, so cite SCA for official totals |
| Open-Meteo | All | Weather features | Free, non-commercial |
| ~~aisstream.io~~ | — | Dropped | 0% coverage of Egyptian waters (tested 2026-10-06) |

## Tech stack (as proposed in Sep 2026)

| Layer | Tools |
|---|---|
| Ingestion | Python collectors (one adapter per source: Port Authority board, GFW, PortWatch/SCA, weather) → Apache Kafka |
| Stream processing | Spark Structured Streaming (PySpark) |
| Storage | Medallion Bronze/Silver/Gold: Parquet on object storage + PostgreSQL |
| Orchestration | Apache Airflow |
| Geospatial / labels | scikit-learn DBSCAN, shapely, geopandas |
| Feature store | Feast |
| Models | XGBoost baseline, optional LSTM |
| Registry / tracking | MLflow |
| Serving | FastAPI (containerized) |
| Monitoring / DQ | Evidently AI, Great Expectations |
| Dashboard | Grafana (ops) + Streamlit or React+Leaflet (product) — see P-003 |
| Infra / CI | Docker Compose, GitHub Actions |

Proposed changes are pending team approval in `docs/decision-log.md` (P-001…P-010). The main ones: drop Cassandra and ELK, add MinIO + PostGIS, and change "drift → rollback" to "drift → retrain, regression → rollback".

## Architecture in one breath

Port Authority board (every 30 min) → collector → Kafka → Spark streaming → shared `features/` library → Feast online store (Redis) → FastAPI → map dashboard.
GFW daily pull + history → Bronze → Airflow → same `features/` library → Gold → Feast offline store → training → MLflow registry (`@champion`/`@challenger`).
Prediction logs + matured labels → monitoring → retrain trigger or alias rollback. The replay simulator re-streams GFW/Bronze history for the Port Said demo and tests.
Full detail: `docs/architecture.md`.

## Conventions (proposed — confirm at kickoff)

- Python 3.11. `ruff` for lint and format, `pytest`, `pre-commit`, type hints on public functions.
- **Time in UTC, ISO-8601.** Coordinates in WGS84 (EPSG:4326). Speed in knots, distance in nautical miles. Port Authority times are Cairo local (DST-aware): convert on ingest.
- **Bronze is immutable raw data.** Partition everything by `date=YYYY-MM-DD/hour=HH`. Use Parquet with zstd.
- **Feature logic lives only in `features/`** and is imported by *both* the batch and streaming jobs. Never re-implement a feature elsewhere.
- **No synthetic data in training or evaluation, ever.** Synthetic data is only for load tests.
- **Time-based splits only.** Every model is reported against the baselines (persistence, seasonal-naive, convoy heuristic).
- Secrets live in `.env` (gitignored): `AISSTREAM_API_KEY`, `GFW_API_TOKEN`. Never paste keys in chat or commit them.
- Git: short-lived branches (`feat/`, `fix/`, `data/`, `docs/`), PR + 1 review, Conventional Commits.
- Any non-trivial decision gets an entry in `docs/decision-log.md`.

## Hard constraints

- **GitHub is docs-only (D-009):** the repo (https://github.com/mohamed-mahmoud-de/RASID, public) holds only `docs/`, `brand/` (images + `BRAND.md`), `README.md`, `CLAUDE.md` and `.gitignore` until the supervisor has reviewed the documents. **Never push code** (`collector/`, `quality/`, `requirements.txt`, `.env.example`, `brand/*.py`, `*.blend` are gitignored).
- **No paid data, no hardware** (team decision 2026-10-06).
- GFW is non-commercial only (CC BY-NC 4.0, attribution "Powered by Global Fishing Watch").
- Poll the Port Authority board politely: ≥ 2 s between requests, at most every 30 min, project named in the User-Agent. Never publish raw scraped data.
- The whole stack must run under docker-compose on one 16 GB machine, using profiles.
- SAR / satellite imagery is out of scope.

## Current status (2026-10-07)

- Docs: **proposal v2 (2026-10-14)** at `docs/proposal/proposal.pdf`: one document with problem statement, solution, competitor analysis and the full SRS requirement list (24 pages). The editable .docx is rebuilt from `build/proposal/` (gitignored); the old Gamma deck and brief were deleted (still in git history). Planning docs in `docs/`; reports in `docs/reports/`.
- Data-source research done. Every free live AIS feed has 0% Egypt coverage; full catalog in `docs/data-sources.md`.
- Local code (not on GitHub):
  - `collector/apa_scraper.py`: Port Authority board → `data/bronze/apa/`
  - `collector/fetch_gfw.py`: GFW presence per named area → `data/bronze/gfw/`, `data/silver/gfw/`
  - `collector/fetch_portwatch.py`
  - `quality/dq_report.py` → `docs/reports/data_quality_report.md`
- **GFW validated:** Port Said covered 24/24 h (~100–130 vessels/h in the port box). **Ever Given 2021:** waiting ships went from ~15 to a peak of 160 (`docs/reports/gfw-validation.md`). Alexandria also covered (~22 stationary ships outside the port per hour).
- **Port Authority board facts:**
  - 40/76 in-port records are > 60 days old (open since 2011–2017).
  - `تاريخ الرسو` looks like the *latest* berth move.
  - Local craft use placeholder IMOs.
  - Berth `مخطاف داخلي` = inner-anchorage queue.
  - The board doesn't show the outer-anchorage queue GFW sees, so the overlap period is needed.
- **Next:** 30-min board poller + daily GFW pull on an always-on machine (O-004); GFW Port Said backfill 2017 → now; anchorage zones and vessel-type enrichment; supervisor letter to APA.

## Next milestones

| ID | Target date | Milestone |
|---|---|---|
| G1 | 2026-10-19 | Board poller + daily GFW pull running 24/7; Port Said history backfilled; target definition (O-001) locked |
| M1 | 2026-11-29 | Thin slice on real data (Port Said, GFW): zones → labels → features → XGBoost beats baselines → FastAPI → map |
| M2 | 2027-01-24 | Streaming features via Feast (Alexandria live); batch/stream parity test green in CI; overlap analysis done |
| M3 | 2027-03-21 | Closed MLOps loop demonstrated (drift → retrain, regression → rollback) + SHAP |
| M4 | 2027-05-09 | Feature freeze; backtests (incl. Ever Given); pilot/customer evidence |
| M5 | ~2027-06 | Thesis + defense (date TBC) |

## Known errors in submitted materials

All fixed. The 9 errors in the first proposal were corrected on 2026-10-09; the proposal was merged into one document on 2026-10-14 (team problem statement + team competitor analysis + SRS requirements, logo v2). The old Gamma deck (unsourced "5.89 days" figure, "6 People") and the old brief (aisstream.io data sources) were deleted on 2026-10-14; a new deck must be built from the current proposal, not from them.

**Still missing:** the UI prototype (team, Figma); the planned screens S1–S9 in proposal §4.2 are placeholders. The proposal source (.docx) is rebuilt with `build/proposal/` (`node build_proposal.js` then `finalize.ps1`).

## Context files

- `docs/README.md` — index and reading order for the supervisor
- `docs/maritime-101.md` — **start here if you're new to shipping**: plain-English explanation of every maritime term
- `docs/data-sources.md` — **catalog of Port Said / Suez data sources** (free vs. paid, real-time vs. historical, tested vs. documented)
- `docs/project-context.md` — domain primer, 2026 Suez situation, glossary, literature, competitors
- `docs/architecture.md` — components, data flow, medallion schemas, API contract, repo layout, deployment
- `docs/data-and-mlops.md` — data sources, cleaning, labels, features, models, evaluation, MLOps loop
- `docs/roadmap.md` — phases, workstreams, task checklists, decision gates
- `docs/decision-log.md` — decided / proposed / open decisions (ADR-lite) and test results
- `docs/meeting-notes.md` — meeting template and log
- `docs/strategy.md` — commercialization, enterprise, startup, production roadmap, team process
- `docs/reports/` — data-quality report (Port Authority board + PortWatch), GFW validation, figures
- `docs/proposal/proposal.pdf` — **the graduation project proposal** (problem statement, solution, competitor analysis, 149 requirements)
- `brand/BRAND.md` — logo, colours, fonts, which file to use where. **Official logo (v2, radar mark + Outfit capitals):** `brand/rasid_logo_v2.png` (covers, slides), `brand/rasid_logo_v2_horizontal.png` (document headers), `brand/rasid_appicon_v2.png` (avatar). v1 logo files deleted 2026-10-14

## Instructions for Claude

- Treat this as a real product. Be direct, practical, and ambitious, and challenge weak assumptions.
- **The team has no maritime background.** Explain shipping terms in plain English the first time they appear, or point to `docs/maritime-101.md`. Don't assume they know AIS, ETA, demurrage, anchorage, etc.
- Check `docs/decision-log.md` before proposing stack or design changes. Log new decisions there.
- **Never push code to GitHub** until the supervisor approves (D-009). Before any push, verify that only docs are tracked and that no secrets are present.
- Never invent statistics. Any number that goes into the deck or thesis needs a source. Use the corrected citations in `docs/project-context.md`.
- Never use synthetic data for training or evaluation.
- Update the "Current status" and milestone sections of this file when they change.
