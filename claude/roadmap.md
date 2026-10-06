# Roadmap & Task Breakdown

Assumes a defense around **June 2027**. Re-baseline these dates once the department publishes the official dates and exam weeks. Weeks run Sunday–Thursday.

## Workstreams & owners

| WS | Scope | Primary | Backup |
|---|---|---|---|
| W1 Ingestion & streaming | Collector, Kafka, Spark streaming, replay simulator, load test | TBD | TBD |
| W2 Storage, quality & orchestration | MinIO/Parquet, Postgres/PostGIS, Airflow DAGs, GE suites, backfills | TBD | TBD |
| W3 Geospatial labeling | Zone detection, gate lines, episodes, labels, PortWatch validation | TBD | TBD |
| W4 Features & modeling | `features/` library, baselines, XGBoost, LSTM, SHAP, evaluation | TBD (**unassigned in proposal**) | TBD |
| W5 MLOps & platform | Feast, MLflow, FastAPI, monitoring/rollback, CI/CD, compose, integration | Mohamed Mahmoud | TBD |
| Product (shared) | Dashboard, customer interviews, deck/thesis integration | Rotating | — |

The four Data Engineers (Youssef Nasser, Youssef Elkomy, Alhassan Mohamed, Reem Adel) choose W1–W4 at kickoff. Every workstream needs a backup so no single absence blocks a milestone.

---

## Phase 0 — Foundations (Oct 6 → Oct 19, 2026) → Gate G1

- [ ] **Collector running 24/7 on an always-on VM**, writing hourly NDJSON.gz to disk or object storage, auto-restart via systemd/Docker `restart: always` *(W1, day 1–3)*
- [ ] Private GitHub repo, branch protection, pre-commit (ruff), CI skeleton, `.env.example`, `CLAUDE.md` + `claude/` committed *(W5)*
- [x] Coverage validation vs IMF PortWatch → **preliminary result: aisstream ≈ 0% coverage of Egypt** (2026-10-06, see decision log) *(W3)*
- [ ] Re-run the 10-min coverage capture at a different time of day to confirm *(W1)*
- [ ] Decide **O-007** (data source for Egyptian waters): price a paid API trial; spec an own-receiver kit (RTL-SDR + 162 MHz antenna + Pi + AIS-catcher); find a rooftop in Alexandria and a host in Port Said *(lead + W1)*
- [ ] Plot two weeks of positions on a map, eyeball the anchorages, draft gate lines *(W3)*
- [ ] Decide O-001 (target queue) and O-002 (horizons) *(all)*
- [ ] Fix the errors in submitted materials (see `CLAUDE.md`) and send the corrected proposal to the supervisor *(lead)*
- [ ] Assign W1–W4 owners and backups *(all)*

## Phase 1 — Thin slice, batch-only, real data (Oct 20 → Nov 29) → M1 + Gate G2

- [ ] docker-compose `core` profile: MinIO, Postgres/PostGIS, Redis *(W2)*
- [ ] Bronze → Silver job + cleaning rules + Silver GE suite *(W2)*
- [ ] Zone detection v1 → `zones/v1.geojson`, reviewed on a map *(W3)*
- [ ] Episode builder + zone-hour Gold table + labels Y1/Y2 *(W3)*
- [ ] `features/` v1 (state, flow, calendar, lags) with unit tests *(W4)*
- [ ] Baselines + XGBoost v1 + rolling-origin evaluation, logged to MLflow *(W4, W5)*
- [ ] FastAPI `/v1/zones/{id}/forecast` reading Gold/latest features *(W5)*
- [ ] Minimal map dashboard *(Product)*
- [ ] **G2:** XGBoost skill vs. persistence > 0 at h = 6 h? If not, revisit the target/horizon *before* Phase 2
- [ ] **M1 demo to supervisor**

## Phase 2 — Streaming + feature store (Nov 30 → Jan 24, 2027) → M2

*Lighter load during January exams.*

- [ ] Kafka (KRaft) + collector → `ais.raw`; Spark Structured Streaming clean + features via `features/` *(W1)*
- [ ] Feast repo: `zone` entity, offline Parquet source, Redis online store, push source from Spark *(W5)*
- [ ] Airflow DAGs:
  - [ ] daily Silver/Gold build
  - [ ] label maturity
  - [ ] Feast materialize
  - [ ] weekly retrain *(W2)*
- [ ] Replay simulator: Bronze window → Kafka at N× speed *(W1)*
- [ ] **Parity test in CI** (24 h fixture, batch vs. stream features) *(W4, W5)*
- [ ] Weather + approach-pressure + propagation features *(W4)*
- [ ] **M2 demo:** live forecasts from streaming features, parity test green

## Phase 3 — Closed MLOps loop + explainability (Feb 1 → Mar 21) → M3

- [ ] Prediction logging (with model version); matured-label performance job *(W5)*
- [ ] Evidently drift job → retrain trigger *(W5)*
- [ ] Champion/challenger with shadow mode; rollback controller (alias move + serving hot-reload) *(W5)*
- [ ] Quantile forecasts (P10/P50/P90) + congestion levels; SHAP drivers in API and dashboard *(W4)*
- [ ] LSTM experiment on the same folds; keep it only if it wins *(W4)*
- [ ] Grafana ops dashboard: feed lag, messages/min, API latency, model MAE *(W2, W5)*
- [ ] **M3 demo:** injected drift → retrain; bad model → rollback, live

## Phase 4 — Validation & hardening (Mar 22 → May 9) → M4 feature freeze

- [ ] Backtests on real events inside the collection window: weather closures, carrier-return surges *(W3, W4)*
- [ ] Decide O-003 (Ever Given window: buy the data or drop the claim) *(lead)*
- [ ] Load test: synthetic 10× traffic through Kafka/Spark (load only, never training) *(W1)*
- [ ] Failure drills: kill the collector, kill Kafka, corrupt a batch. Document recovery *(W2)*
- [ ] Docs: architecture, runbook, model card, data card *(all)*
- [ ] Customer evidence: interview summary + a pilot or letter of intent if possible *(Product)*

## Phase 5 — Thesis & defense (May 10 → defense)

- [ ] Thesis chapters merged. Each workstream has been drafting its chapter since Phase 1
- [ ] Final deck (no Gamma badge, every stat cited), live demo + recorded fallback video
- [ ] Two full rehearsals with supervisor Q&A drills (use the proposal's Q&A list plus the hard questions in `decision-log.md`)

## Business track (parallel, ~2 h/week)

- **Nov–Feb:** 15–20 discovery interviews with shipping agents and forwarders in Alexandria/Port Said, plus terminal planners, bunker suppliers, and ship chandlers. Rotate the interviewer and log notes in `meeting-notes.md`.
- **Feb–Apr:** one pilot partner who shares actual anchorage/berth timestamps. This **validates the AIS-derived labels** (the proposal's biggest academic weakness) and produces the commercial case study.
- **Throughout:** a public weekly "Egypt Gateway Congestion Index" post (LinkedIn) as an audience and credibility builder.
