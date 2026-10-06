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

## Decided (team decisions after the Sep 2026 proposal)

| ID | Date | Decision | Why | Consequence |
|---|---|---|---|---|
| **D-008** | 2026-10-07 | **Data sources (free only: no paid data, no hardware):**<br>• **Port Said / Suez Canal (main analysis):** Global Fishing Watch AIS vessel presence (hourly, per vessel, ~1 km cells, 2017 → ~5 days ago) for **training, labels (anchorage queue, waiting time) and backtesting** of 6–12 h forecasts, including the 2021 Ever Given event. It is not live, so the Port Said demo uses the **replay simulator**.<br>• **Alexandria (live showcase):** Alexandria Port Authority ship board polled **every 30 min** as the **live** source, plus GFW Alexandria history for training. **4–6 weeks of side-by-side collection** to align the two before live predictions.<br>• **Validation and context:** IMF PortWatch (daily), Suez Canal Authority (monthly official totals, daily bulletins), Open-Meteo (weather).<br>• **aisstream.io dropped** (0% Egypt coverage) | No free live AIS covers Egypt (tested). GFW passed the Port Said coverage and Ever Given tests. The Alexandria board is the only free live official source | Start APA polling and a daily GFW pull immediately. Build anchorage zones and vessel-type enrichment (GFW types are coarse). GFW is CC BY-NC 4.0, non-commercial only, so a company would need another source. Request written APA permission via the supervisor. **Supersedes P-011; resolves O-007 and O-003; D-001 now applies to Port Said only** (Alexandria labels come from official times) |
| **D-009** | 2026-10-07 | **The GitHub repo holds documents only** (in `docs/`) until the supervisor has reviewed them. Code stays local and is gitignored | The supervisor reviews the documents first | Never push code until approved; history before 2026-10-07 contains early scripts |

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
| P-011 (2026-10-06) → **accepted as D-008** | **New data plan, all free:**<br>(a) **Live stream:** poll the Alexandria Port Authority ship-status system every 15–30 min, store snapshots in Bronze, emit change events (arrived, berthed, departed, new expected) to Kafka.<br>(b) **AIS history and context:** Global Fishing Watch hourly per-ship presence around Alexandria and Port Said (batch, daily). This also gives the 2021 Ever Given window for free.<br>(c) Weather: Open-Meteo.<br>(d) Validation: PortWatch + alexcont ATA/ATB.<br>MVP port becomes **Alexandria**; Port Said via GFW (delayed) | No free live AIS covers Egypt. The port system gives **official** arrival and berthing times, which are better labels than AIS-derived ones. Must poll politely and seek written permission from APA (via the supervisor). The GFW license is non-commercial only (fine for the thesis; a startup would need a license) |

## Open

| ID | Question | Options | Decide by |
|---|---|---|---|
| O-001 | Which queue is the MVP target? | (a) Canal-approach wait at Port Said North Anchorage (convoy-driven, highest volume); (b) port berth wait at East/West Port Said (berth-driven, closer to terminal customers) | G1, 2026-10-19 |
| O-002 | Forecast horizons | 6/12/24 h (proposed); check what customers actually need | G1 |
| O-003 | ~~Ever Given (2021) backtest~~ **Resolved by D-008:** GFW covers Mar–Apr 2021 for free (tested) | — | Done |
| O-004 | Always-on hosting **for the 30-min Alexandria poller and the daily GFW pull** | Azure for Students / GitHub Student Pack credits / Oracle free tier / university server | This week |
| O-005 | Product dashboard tech | Streamlit (fast) vs. React+Leaflet (product-grade) | Phase 1 |
| O-006 | Product name | "Rasid" (folder name)? | Any time |

## Results & findings

| Date | Check | Result | Consequence |
|---|---|---|---|
| 2026-10-06 | **G1 coverage check (preliminary)**: 10-min capture over the Egypt box (lat 29.5–33.5, lon 29.5–34.5) + 5-min probe over East Med/Red Sea (lat 12–37.5, lon 25–45) | **aisstream.io sees 0 vessels at Port Said, in the canal, at Damietta, Alexandria, the Gulf of Suez, or the Red Sea.** The only "Egypt box" hits are ships anchored off Ashdod, Israel. The probe saw hundreds of vessels, all off south Turkey, Cyprus, and Israel. Meanwhile IMF PortWatch reports ~40 Suez transits/day. Coverage of our target ≈ **0%** | **The free feed fails G1 for Egyptian waters.** Re-run at a different time of day to confirm, then decide O-007. Raw files: `data/bronze/sample/`, `data/bronze/coverage_probe/` |
| 2026-10-06 | **Free-data deep search** (constraint: no paid data, no hardware) | Live AIS networks: aisstream ✗; **Open Waters AIS** (aisstream + AISHub + volunteers, anonymous) ✗, since its only live Egypt-box ships are off Ashdod and El Arish/Port Said sightings were 56–65 h old (sporadic long-range); AISHub ✗ (needs own antenna); VesselAPI ✗ (150 calls/month); VesselFinder/Vessels API/Datalastic ✗ (trial/paid). **Found:** (1) **Alexandria Port Authority live system** `spsonlinealex.apa.gov.eg` (public, no login): expected / in-port / departed ships with IMO, type, agent, **actual arrival, berth, berthing time**, departure, cargo type and tonnage, origin/destination. (2) **Global Fishing Watch AIS presence API**: free non-commercial, satellite+terrestrial AIS, all vessel types (CARGO, BUNKER_OR_TANKER…), HOURLY, 0.01° cells, group by MMSI, speed filter, 2012 → ~3–4 days ago. (3) alexcont.com berthing situation (container terminals: ETA/ATA/ATB/ETC, daily). (4) Damietta: daily press bulletins only | See proposal P-011 |
| 2026-10-06 | **Port Said / Suez live-source check** | No free live source for Port Said or the canal. SCZONE publishes no public ship board; APM Terminals (SCCT) APIs are for customers only; the Suez Canal Authority publishes daily totals only via news; Voyage Radar's free tier is 500 one-time credits; VesselFinder port pages don't allow scraping. **Coverage by source:** GFW = Port Said + canal + Alexandria (hourly, 3–4 days late); APA board = Alexandria/Dekheila only (live); PortWatch = canal transits + port calls (daily counts, a few days late) | Live predictions are only possible for Alexandria. Port Said/Suez congestion is batch-only (GFW + PortWatch) |
| 2026-10-07 | **GFW validation (token obtained)** | Works for Port Said: 92–133 vessels present per hour in the port box, 197 vessels/day, 24/24 hours covered. Latest data = 2026-10-02 on 2026-10-07, so **~5 days latency**. **Ever Given test (Mar 9 – Apr 12, 2021):** 840/840 hours with data. Waiting (stationary) vessels in the northern anchorage went from a baseline of ~14.5 to a **peak of 160 at 2021-03-29 11:00 UTC**, cleared by ~Apr 11, matching the known timeline. Weak point: vessel types are coarse (57% "OTHER"; e.g. a Scorpio tanker labelled OTHER) | **GFW is GO as the Port Said training/backtest source.** Not a live source. Need type enrichment + proper anchorage zones. Figure: `docs/reports/figures/gfw_port_said_ever_given.png` |
| 2026-10-07 | **Can GFW history + APA live drive live Alexandria predictions?** | GFW covers Alexandria well: 168/168 h, 209 vessels/week, ~48 inside ports and ~27 outside per hour (~22 stationary outside). But the APA board shows only 1 ship at the inner anchorage and 6 "ETA passed" expected ships, so **the two sources measure different things**. Only 12/19 recent board ships matched GFW by IMO | **Yes, but only after a 4–6 week side-by-side overlap** to map board features onto GFW features (or use features both can produce: arrivals/hour, ships at berth, expected arrivals next 12 h, time, weather). PortWatch = daily checks only. Start APA polling now |
| 2026-10-06 | PortWatch reference pull | Suez daily transits Oct 2025–Oct 2026: flat ~40–43/day; Port Said ~2 port calls/day, Damietta ~7, Alexandria ~8 (Sep 2026) | Ground-truth benchmark saved to `data/reference/` |

## Open (added 2026-10-06)

| ID | Question | Options | Decide by |
|---|---|---|---|
| O-007 | ~~**Where does Egyptian AIS come from?**~~ **Resolved by D-008** (GFW + Alexandria board; no paid data, no hardware). Options kept for the record: | (a) **Own receiver(s):** AIS-catcher (MIT, free) + RTL-SDR dongle (~$25–40) + 162 MHz antenna + Pi/PC on a high rooftop. Range depends on antenna height: ~15–20 nm at 15 m, ~25 nm at 20 m, 40–60 nm for elevated base stations (MarineTraffic support). So Alexandria is reachable by the team itself; Port Said needs a host there. AIS-catcher forwards live messages over UDP/TCP/HTTP, so we decode them with `pyais` in a collector adapter. Sharing the feed with AISHub unlocks their API (JSON, bounding-box query, max 1 request/min), but whether AISHub has any Egyptian stations is **unverified**. Check NTRA/customs rules for importing and using an SDR receiver, and buy locally if possible. (b) **Paid API**: Datalastic (REST only, "area traffic scan" + historical endpoints, plans by credits, 14-day money-back; price to confirm, team estimate ~€80/mo), DataDocked, MarineTraffic/Kpler, Spire (satellite; ask about academic access). Covers Port Said immediately; we poll every ~60 s via a collector adapter, which matches the ~1 report/min/vessel cadence we observed anyway. (c) **Re-scope MVP to Alexandria/Dekheila** with own receiver, keeping Port Said as the multi-port phase. (d) Combination: paid API for Port Said now + own receiver for Alexandria as the proprietary-data moat | G1, 2026-10-19 |

## Hard questions to prepare for (defense)

- "Your labels come from AIS. How do you know they're correct?" → PortWatch cross-check, manual review of 50 episodes, pilot-partner timestamps.
- "Does the model beat a trivial baseline?" → skill vs. persistence and the convoy heuristic, per horizon.
- "Why Spark/Kafka for this data volume?" → multi-port scalability and the department's DE requirement. Show the 10× load test.
- "What happens when traffic patterns shift (Red Sea return)?" → drift monitoring, retraining, metrics per regime.
