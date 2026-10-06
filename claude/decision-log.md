# Decision Log (ADR-lite)

Format: ID · date · decision · why · consequences. Statuses:
- **Decided**: agreed in the proposal.
- **Proposed**: suggested, awaiting team vote.
- **Open**: needs data or a decision.

Never delete an entry. Supersede it with a new one.

## Decided (from the Sep 2026 proposal)

| ID | Decision | Why | Consequence |
|---|---|---|---|
| D-001 | Derive features **and** labels from AIS only | No port-authority data access; Peng et al. (2023) method is peer-reviewed | Label quality must be validated (PortWatch, pilot partner) |
| D-002 | Medallion Bronze/Silver/Gold layout | Reproducibility; raw data preserved | Bronze is immutable and kept forever |
| D-003 | Batch + streaming paths bridged by a feature store (Feast) | Eliminate train–serve skew | Requires a shared feature library (see P-001) |
| D-004 | XGBoost baseline, LSTM optional | Tabular strength, explainability, small data | LSTM only if it beats XGBoost on the same folds |
| D-005 | Real data only for training/eval; synthetic only for load tests | Synthetic ships = invented congestion | Replay simulator uses real Bronze data |
| D-006 | SAR/satellite imagery out of scope | Cost, ~6-day revisit | Possible future "dark vessel" feature |
| D-007 | Start with one gateway (Port Said / canal approach), expand later | Thin slice first | Pipeline parameterized by bbox + zone set |

## Proposed (by Claude on 2026-10-06; vote at kickoff)

| ID | Proposal | Rationale |
|---|---|---|
| P-001 | All feature transforms live in one `features/` library imported by both Spark streaming and Airflow batch. Feast handles storage, point-in-time retrieval, and online serving | Feast doesn't compute features. Parity comes from shared code. Proven by a CI parity test |
| P-002 | Replace "drift → rollback" with **"drift → retrain; performance regression → rollback"**, using champion/challenger + shadow mode | Rolling back to an older model doesn't fix a changed world. Labels are delayed by days, so performance must be measured on matured labels |
| P-003 | Drop Cassandra. Drop Elasticsearch/Kibana. Use **Grafana** for ops and **Streamlit or React+Leaflet** for the product map | Data volume is small (one region). ELK duplicates Grafana and costs a lot of RAM. Fewer moving parts = more time on the model |
| P-004 | Add **MinIO** (S3-compatible) for Parquet and **PostGIS** for zone geometry | Cloud migration becomes a config change. Spatial joins in SQL |
| P-005 | Mandatory baselines: persistence, seasonal-naive, **convoy-schedule heuristic** | If ML can't beat "wait for the next convoy", the model adds nothing. Examiners will ask |
| P-006 | Start the raw collector **now**, on an always-on VM, independent of Kafka | History is unrecoverable. Kafka can be added later in front of the same collector |
| P-007 | Use **IMF PortWatch** for coverage validation and daily-level backtests | Free, official-grade, daily data since 2019 |
| P-008 | Use MLflow **aliases** (`@champion`, `@challenger`, `@previous`), not stages | Stages are deprecated. Rollback = moving an alias |
| P-009 | Quantile forecasts (P10/P50/P90) instead of point forecasts | Operators plan against risk. Intervals build trust |
| P-010 | Collect a wide bbox (Alexandria → Suez) from day 1; model Port Said first | Storage is cheap. This builds the multi-port dataset for later |

## Open

| ID | Question | Options | Decide by |
|---|---|---|---|
| O-001 | Which queue is the MVP target? | (a) Canal-approach wait at Port Said North Anchorage (convoy-driven, highest volume); (b) port berth wait at East/West Port Said (berth-driven, closer to terminal customers) | G1, 2026-10-19 |
| O-002 | Forecast horizons | 6/12/24 h (proposed); check what customers actually need | G1 |
| O-003 | Ever Given (2021) backtest | Buy vessel-level AIS for Mar–Apr 2021 (~€80+), or replace with in-window events (weather closures, carrier-return surges) | Phase 4 |
| O-004 | Always-on hosting | Azure for Students / GitHub Student Pack credits / Oracle free tier / university server | This week |
| O-005 | Product dashboard tech | Streamlit (fast) vs. React+Leaflet (product-grade) | Phase 1 |
| O-006 | Product name | "Rasid" (folder name)? | Any time |

## Results & findings

| Date | Check | Result | Consequence |
|---|---|---|---|
| 2026-10-06 | **G1 coverage check (preliminary)**: 10-min capture over the Egypt box (lat 29.5–33.5, lon 29.5–34.5) + 5-min probe over East Med/Red Sea (lat 12–37.5, lon 25–45) | **aisstream.io sees 0 vessels at Port Said, in the canal, at Damietta, Alexandria, the Gulf of Suez, or the Red Sea.** The only "Egypt box" hits are ships anchored off Ashdod, Israel. The probe saw hundreds of vessels, all off south Turkey, Cyprus, and Israel. Meanwhile IMF PortWatch reports ~40 Suez transits/day. Coverage of our target ≈ **0%** | **The free feed fails G1 for Egyptian waters.** Re-run at a different time of day to confirm, then decide O-007. Raw files: `data/bronze/sample/`, `data/bronze/coverage_probe/` |
| 2026-10-06 | PortWatch reference pull | Suez daily transits Oct 2025–Oct 2026: flat ~40–43/day; Port Said ~2 port calls/day, Damietta ~7, Alexandria ~8 (Sep 2026) | Ground-truth benchmark saved to `data/reference/` |

## Open (added 2026-10-06)

| ID | Question | Options | Decide by |
|---|---|---|---|
| O-007 | **Where does Egyptian AIS come from?** (aisstream has no coverage) | (a) **Own receiver(s):** AIS-catcher (MIT, free) + RTL-SDR dongle (~$25–40) + 162 MHz antenna + Pi/PC on a high rooftop. Range is roughly 20–40 nm, so Alexandria is reachable by the team itself; Port Said needs a host there. Feed AISHub to get network access back. Check NTRA rules for receive-only equipment. (b) **Paid API** (Datalastic/DataDocked ~€80/mo, MarineTraffic/Kpler, Spire), which covers Port Said immediately. (c) **Re-scope MVP to Alexandria/Dekheila** with own receiver, keeping Port Said as the multi-port phase. (d) Combination: paid API for Port Said now + own receiver for Alexandria as the proprietary-data moat | G1, 2026-10-19 |

## Hard questions to prepare for (defense)

- "Your labels come from AIS. How do you know they're correct?" → PortWatch cross-check, manual review of 50 episodes, pilot-partner timestamps.
- "Does the model beat a trivial baseline?" → skill vs. persistence and the convoy heuristic, per horizon.
- "Why Spark/Kafka for this data volume?" → multi-port scalability and the department's DE requirement. Show the 10× load test.
- "What happens when traffic patterns shift (Red Sea return)?" → drift monitoring, retraining, metrics per regime.
