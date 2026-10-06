# CLAUDE.md — Rasid: Smart Port & Maritime Congestion Predictor

> Persistent project memory for Claude Code sessions. Keep this file short and current; details live in `claude/`.
> Last updated: 2026-10-06

**Working name:** Rasid (راصد — Arabic for "observer"), taken from the project folder name. *Confirm with team.*
**Formal title:** Smart Port & Maritime Congestion Predictor — An AIS-Based Predictive Data Engineering & MLOps Pipeline for Egyptian Maritime Gateways.

## What this is

- **Goal:** forecast near-term vessel congestion (anchorage waiting time + a congestion index) at the Port Said / northern Suez Canal approach, 6–24 h ahead, so operators plan *before* the queue forms.
- **Problem:** congestion at Egyptian gateways is handled reactively. Waiting at anchorage costs demurrage, detention, fuel, and missed downstream logistics.
- **Key design decision:** both features *and* ground-truth labels are derived from AIS alone. DBSCAN + convex hull find the anchorage and berth zones, then nav status + speed + timestamps give the waiting times. This follows Peng et al. (2023), so no port-authority data is needed.
- **Novel contribution:** this AIS congestion method applied to Egyptian gateways, plus real-time streaming and production MLOps (feature store, registry, drift monitoring, rollback). The proposal claims nobody has combined these for this corridor.
- **Two identities:** it is a DE + MLOps graduation project *and* a product candidate. Make decisions that serve both.

## Academic context

- Alexandria University, **Faculty of Science, SIM (Software Industry & Multimedia) Department**
- Supervisor: **Prof. Mohamed Kholief**
- Department requirement: Data Engineering + MLOps project
- Academic year 2026/27. Defense date TBC, roadmap assumes ~June 2027.

## Team (authoritative roster: 5 people)

| Member | Role | Owns |
|---|---|---|
| Mohamed Mahmoud | **Team Leader**, Data Engineer & MLOps Engineer | W5 MLOps & platform; integration; supervisor liaison |
| Youssef Nasser | Data Engineer | Workstream TBD |
| Youssef Elkomy | Data Engineer | Workstream TBD |
| Alhassan Mohamed | Data Engineer | Workstream TBD |
| Reem Adel | Data Engineer | Workstream TBD |

Workstreams W1–W5 are defined in `claude/roadmap.md`. **Gap:** the proposal assigns no one to modeling and evaluation (W4). Assign an owner.

## Tech stack (as proposed in Sep 2026)

| Layer | Tools |
|---|---|
| Ingestion | Python WebSocket client (aisstream.io) → Apache Kafka |
| Stream processing | Spark Structured Streaming (PySpark) |
| Storage | Medallion Bronze/Silver/Gold: Parquet on object storage + PostgreSQL |
| Orchestration | Apache Airflow |
| Geospatial / labels | scikit-learn DBSCAN, shapely, geopandas |
| Feature store | Feast |
| Models | XGBoost baseline, optional LSTM |
| Registry / tracking | MLflow |
| Serving | FastAPI (containerized) |
| Monitoring / DQ | Evidently AI, Great Expectations |
| Dashboard | Kibana *or* Grafana *or* Streamlit (undecided) |
| Infra / CI | Docker Compose, GitHub Actions |

Proposed changes are pending team approval in `claude/decision-log.md` (P-001…P-010). The main ones: drop Cassandra and ELK, add MinIO + PostGIS, and change "drift → rollback" to "drift → retrain, regression → rollback".

## Architecture in one breath

Live AIS → collector → Kafka → Spark streaming → shared `features/` library → Feast online store (Redis) → FastAPI → map dashboard.
Bronze history → Airflow → same `features/` library → Gold → Feast offline store → training → MLflow registry (`@champion`/`@challenger`).
Prediction logs + matured labels → monitoring → retrain trigger or alias rollback. A replay simulator re-streams recorded Bronze data for tests and the demo.
Full detail: `claude/architecture.md`.

## Conventions (proposed — confirm at kickoff)

- Python 3.11. `ruff` for lint and format, `pytest`, `pre-commit`, type hints on public functions.
- **Time in UTC, ISO-8601.** Coordinates in WGS84 (EPSG:4326). Speed in knots, distance in nautical miles.
- **Bronze is immutable raw data.** Partition everything by `date=YYYY-MM-DD/hour=HH`. Use Parquet with zstd.
- **Feature logic lives only in `features/`** and is imported by *both* the batch and streaming jobs. Never re-implement a feature elsewhere.
- **No synthetic data in training or evaluation, ever.** Synthetic data is only for load tests.
- **Time-based splits only.** Every model is reported against the baselines (persistence, seasonal-naive, convoy heuristic).
- Secrets live in `.env` (gitignored). Commit a `.env.example`.
- Git: short-lived branches (`feat/`, `fix/`, `data/`, `docs/`), PR + 1 review, Conventional Commits.
- Any non-trivial decision gets an entry in `claude/decision-log.md`.

## Hard constraints

- **aisstream.io:** free, **no SLA, events not durably replayed**, max 3 connections per account and per IP, commercial terms unpublished. **Measured coverage of Egyptian waters ≈ 0% (2026-10-06).** Persist raw data immediately and never depend on it for history.
- Budget ≈ zero. Optional paid backfill is ~€80/month (Datalastic / DataDocked).
- The whole stack must run under docker-compose on one 16 GB machine, using profiles.
- SAR / satellite imagery is out of scope.

## Current status (2026-10-06)

- Done: proposal (.docx), project brief (.md), 10-slide deck (Gamma PDF).
- Done: `collector/capture_sample.py` (aisstream → Bronze NDJSON), `collector/summarize_sample.py`, `collector/build_viz_data.py`. API key in `.env` (gitignored).
- Done: IMF PortWatch reference data in `data/reference/` (Suez daily transits, 1 year; Port Said/Damietta/Alexandria daily port calls).
- 🚨 **Blocking finding (2026-10-06):** aisstream.io has **~0% coverage of Egyptian waters**. In live tests, zero vessels appeared at Port Said, the canal, Damietta, Alexandria, or the Red Sea, while PortWatch reports ~40 transits/day. Its receivers in the region are in south Turkey, Cyprus, and Israel. The data-source decision is open as **O-007** in `claude/decision-log.md` (own receiver vs. paid API vs. re-scope to Alexandria).
- Not started: git repo, continuous collection (pointless on aisstream until O-007 is decided).

## Next milestones

| ID | Target date | Milestone |
|---|---|---|
| G1 | 2026-10-19 | Collector live 24/7; coverage go/no-go vs IMF PortWatch; target definition locked |
| M1 | 2026-11-29 | Thin slice on real data: zones → labels → features → XGBoost beats baselines → FastAPI → map |
| M2 | 2027-01-24 | Streaming features via Feast; batch/stream parity test green in CI |
| M3 | 2027-03-21 | Closed MLOps loop demonstrated (drift → retrain, regression → rollback) + SHAP |
| M4 | 2027-05-09 | Feature freeze; backtests; pilot/customer evidence |
| M5 | ~2027-06 | Thesis + defense (date TBC) |

## Known errors in submitted materials (fix before the next submission)

1. **Team size:** the proposal lists 6 names, with "Mohamed Mahmoud" appearing twice ("Mohamed Mahmoud Ahmed" and "Mohamed Mahmoud (Zane) — MLOps Lead"). The brief says 6 and the deck says "6 People" but shows 4 DE + 1 MLOps. The real team is **5**.
2. **Faculty:** the proposal cover says "Faculty of Computer & Data Science". It should be **Faculty of Science, SIM Department**.
3. **Names to confirm:** "Ream Adel Mohamed" vs Reem Adel; "Youssef Mohamed Mostafa", assumed to be Youssef Elkomy.
4. **Peng citation:** it should read Peng, W., Bai, X., Yang, D., Yuen, K. F., & Wu, J. (**2023**), *Maritime Policy & Management*, 50(7), 835–860. The proposal has "Peng, P. … 2022".
5. **PLOS One paper** (Chico et al., 2025, doi:10.1371/journal.pone.0320129): the zone near Port Said is the **North Anchorage**. The South Anchorage is near Suez port. The proposal has this backwards.
6. **"5.89 days median wait"** (deck slide 2): no source found, and it is not in the PLOS paper. Cite it or remove it.
7. **Leftover scope:** the proposal's risk table says "if Alexandria alone is too sparse". The scope is Port Said.
8. **Ever Given backtest:** this needs 2021 vessel-level AIS, which is not freely available. Buy the data window or replace the claim (see decision log O-003).
9. The Kaggle AIS backfill probably doesn't cover Suez. Most public AIS sets are US or Danish.
10. The MIT thesis (Budiman, 2024) reference has not been verified yet.

## Context files

- `claude/maritime-101.md` — **start here if you're new to shipping**: plain-English explanation of every maritime term
- `claude/project-context.md` — domain primer, 2026 Suez situation, glossary, literature, competitors
- `claude/architecture.md` — components, data flow, medallion schemas, API contract, repo layout, deployment
- `claude/data-and-mlops.md` — data sources, coverage validation, cleaning, labels, features, models, evaluation, MLOps loop
- `claude/roadmap.md` — phases, workstreams, task checklists, decision gates
- `claude/decision-log.md` — decided / proposed / open decisions (ADR-lite)
- `claude/meeting-notes.md` — meeting template and log
- `claude/strategy.md` — commercialization, enterprise, startup, production roadmap, team process

## Instructions for Claude

- Treat this as a real product. Be direct, practical, and ambitious, and challenge weak assumptions.
- **The team has no maritime background.** Explain shipping terms in plain English the first time they appear, or point to `claude/maritime-101.md`. Don't assume they know AIS, ETA, demurrage, anchorage, etc.
- Check `claude/decision-log.md` before proposing stack or design changes. Log new decisions there.
- Never invent statistics. Any number that goes into the deck or thesis needs a source. Use the corrected citations in `claude/project-context.md`.
- Never use synthetic data for training or evaluation.
- Update the "Current status" and milestone sections of this file when they change.
