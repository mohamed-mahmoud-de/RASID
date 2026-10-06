# Data Pipeline & MLOps Notes

## 1. Data sources (decision D-008, 2026-10-07)

| Source | Port | Use | Facts & risks | Role |
|---|---|---|---|---|
| **Global Fishing Watch, AIS vessel presence** | Port Said / Suez + Alexandria | Hourly per-vessel positions (~1 km cells), 2017 → ~5 days ago | Free, CC BY-NC 4.0 (non-commercial). **Validated:** Port Said 24/24 h coverage, ~100–130 vessels/h; the Ever Given queue spike was captured (baseline ~15 → peak 160 waiting ships). Coarse vessel types (57% "OTHER") | **Primary training / labels / backtests** |
| **Alexandria Port Authority board** | Alexandria | Live expected / in-port / departed ships with official arrival, berthing, departure times, cargo | Free and public, but no API (web extraction) and permission is being requested. Messy legacy records. No history until we collect it | **Primary live source** (Alexandria) |
| **IMF PortWatch** | Suez + Port Said / Alexandria / Damietta | Daily transits / port calls (2019 →) | Free; daily only; trend disagrees with SCA | Validation, daily context |
| **Suez Canal Authority** | Suez | Monthly official totals (reports), daily bulletins (press) | Official; no waiting-time data | Validation |
| **Open-Meteo** (forecast + marine) | All | Wind, gusts, wave height | Free (non-commercial) | Features |
| ~~aisstream.io~~ | — | — | **Dropped: 0% coverage of Egyptian waters** (tested 2026-10-06) | — |

The sections below about the aisstream collector and gate G1 are kept as a **record of the coverage test** that led to D-008. The cleaning rules and the observed AIS facts still apply to any AIS source, GFW included.

### Collector subscription (start wide, model narrow) — historical (aisstream test)

- **Bbox A (core):** lat 29.8–31.8, lon 31.7–32.9. Port Said approaches, the canal, and Suez bay.
- **Bbox B (approaches + other gateways):** lat 30.8–33.5, lon 29.5–34.5. Alexandria, Damietta, and the Med approach lanes.
- **Message types:** PositionReport, StandardClassBPositionReport, ShipStaticData. Optionally also BaseStationReport, which helps diagnose receiver coverage.
- These boxes are starting values. Tune them after week-1 data. Storage is cheap and missed history cannot be recovered, so collect wide.

### Week-1/2 coverage validation (gate G1)

1. Measure messages/hour, unique MMSIs/day, and the median gap between reports for anchored vessels.
2. Draw the canal-entrance gate line. Count unique MMSIs crossing it per day and compare with **PortWatch daily Suez transit calls** (~41/day through 2026; saved in `data/reference/portwatch_suez_daily.json`).
3. Decide based on the coverage ratio:
   - **≥ 70%:** go.
   - **30–70%:** go, but document the bias and add a paid backfill or receiver plan.
   - **< 30%:** escalate. Options are a paid feed, our own AIS receiver, or a scope change.
4. Record the result in the decision log.

## 2. Cleaning rules (Bronze → Silver)

- Drop invalid positions:
  - lat = 91, lon = 181, or coordinates out of range
  - SOG = 102.3 → null (not available)
  - heading = 511 → null
  - COG = 360 → null
- MMSI must have 9 digits and a ship MID prefix (2xx–7xx). Quarantine anything else to a reject table rather than deleting it.
- Dedupe on (mmsi, ts, lat, lon). Drop timestamps in the future (> now + 5 min).
- **Teleport filter:** drop a point if the implied speed from the previous point exceeds 50 kn.
- Filter vessel types to cargo, tanker, container, and bulk (static type 70–89). Keep the rest in Silver, but flagged.
- Join static data (type 5 messages) by MMSI, keeping the latest value per day.

### Observed in real aisstream data (2026-10-06, 720 messages; profile in `data/derived/field_profile.json`)

- **NavStatus lies.** 86 of 149 reports saying "under way using engine" (0) were stationary (< 0.5 kn). Status 1 "at anchor" was always stationary when set, but most stationary ships don't set it. **Detect anchoring from SOG + geofence**; NavStatus is a supporting feature only.
- **Sentinels are common:**
  - TrueHeading 511: 26%
  - RateOfTurn −128: 24%
  - COG 360: 12%
  - SOG 102.3: 2.6%
  - Timestamp ≥ 60: 1.9%
  - ETA hour 24 / minute 60 also appear
- **Cadence:** a median ~60–70 s between received reports per vessel (moving or stationary). That is far sparser than the AIS spec (2–10 s when moving), so receiver/aggregator thinning is real. Design features for ~1 report/min.
- **Latency:** feed delay median 0.55 s, max 8.7 s. Real-time enough.
- **Static data:** within a 5–10 min window only 30% of Class A vessels had sent `ShipStaticData` (it is broadcast every ~6 min). **Keep a persistent vessel registry**, joined by MMSI.
- **ETA/destination are crew-typed and stale:**
  - 79% of set ETAs were already past.
  - 28% of set ETAs were more than 2 weeks old.
  - IMO placeholder `123456789` seen; an 8-digit MMSI seen.
- **Text fields are space-padded** (`"JAMAICA CASTLE      "`). Trim on ingest.
- `MMSI_String` is actually an integer.
- MetaData lat/lon equals the body lat/lon rounded to 5 decimals.
- **Class B (small craft) is ~half the messages** (pleasure 37, sailing 36). Filter out for congestion modeling.

## 3. Labels: the most important design work

**By port (D-008):**
- **Port Said / Suez:** labels are derived from **GFW hourly presence**. Occupancy = vessels stationary in the anchorage zone each hour; an episode = consecutive stationary hours of one vessel in the zone (1-hour resolution, ~1 km cells). The episode rules below apply at hourly granularity.
- **Alexandria:** labels come from **official times** on the Port Authority board (arrival → berthing → departure). They're reconstructed from 30-minute snapshot diffs, because the board's "berthing date" looks like the *latest* berth move (see `reports/data_quality_report.md`).

**Anchorage episode (per vessel):**
- **Start:** the first point inside an anchorage polygon with SOG < 1 kn, sustained ≥ 30 min. NavStatus = 1 supports this but is not required.
- **End:** the vessel leaves the polygon with SOG > 2 kn, *or* crosses a gate line.
- **Wait** = end − start.
- **Flag, don't silently drop:**
  - waits < 1 h (pass-through)
  - waits > 14 days (laid-up, arrested, or bunkering-only vessels)
  - episodes with gaps > 6 h

**Zone-hour tables** (hourly, per zone):
- `occupancy(t)`: vessels inside an open episode at time t
- `arrivals(t)`, `departures(t)`
- `median_wait_completed(t)`
- `median_wait_by_arrival(t)`: the realized wait of vessels that arrived in [t, t+1h)

**Targets (MVP):**
- **Y1** = `occupancy(t+h)` for h ∈ {6, 12, 24}
- **Y2** = `median_wait_by_arrival(t)`, read as "expected wait if you arrive now"
- **Congestion index:** the percentile of occupancy vs. a trailing 90-day distribution, bucketed into LOW / NORMAL / HIGH / SEVERE

**Censoring and label delay:** Y2 for hour t is only known once *all* vessels that arrived in that hour have left, which can take days.
- Use a **label maturity lag** (e.g. 7 days) and only train or evaluate on matured hours. Monitoring has the same delay.
- Optional upgrade: survival models for per-vessel waits.

**Open decision O-001:** canal-approach wait (convoy-driven) vs. port berth wait (berth-driven). Decide after looking at 2 weeks of real data. Don't mix the two.

## 4. Feature catalog v1 (all defined in `features/`)

| Group | Features |
|---|---|
| State | occupancy_now, occupancy_by_vessel_type, mean_elapsed_wait_of_current_queue |
| Flow | arrivals_{1,3,6,24}h, departures_{1,3,6,24}h, net_flow_6h, gate_crossings_6h |
| Approach pressure | vessels inbound within 25/50/100 nm (SOG > 5 kn, heading toward zone), their mean SOG, ETA-to-zone histogram |
| Propagation (Peng et al.) | occupancy at the Suez South Anchorage / Red Sea approach, and at Damietta/Alexandria anchorages |
| Calendar | hour, day of week, Egyptian public holidays, Ramadan flag, convoy-cycle phase (once the SCA schedule is confirmed) |
| Weather | wind speed/gust, wave height at the zone centroid (Open-Meteo), plus a port-closure flag if derivable |
| Lags | target lags 1/6/24/168 h, rolling median waits 24 h/7 d |

**Note:** winter storms close Egyptian ports occasionally. These are real congestion events *inside* our collection window, so log them as backtest events.

## 5. Models

1. **Baselines (must be beaten, always reported):**
   - persistence (y(t+h) = y(t))
   - seasonal-naive (same hour last week)
   - **convoy heuristic**: wait = time until the next convoy that has capacity
2. **XGBoost**, one model per horizon (direct strategy), with a quantile objective (`reg:quantileerror`) for P10/P50/P90.
3. **LSTM** (stretch), on sequences of zone-hour vectors. Keep it only if it beats XGBoost on the same folds.
4. **SHAP** for top drivers per forecast.

## 6. Evaluation protocol

- **Rolling-origin backtest:** expanding window, weekly folds. **No random splits.**
- **Metrics per horizon:**
  - MAE and RMSE
  - **skill vs. persistence**: 1 − MAE_model / MAE_persistence
  - pinball loss
  - P10–P90 interval coverage (target ≈ 80%)
- **Event metrics:** for HIGH/SEVERE onsets, report precision, recall, and **median lead time** (hours of warning).
- **Report by regime:** before vs. after major carrier returns, and weather events.
- **Gate G2 (end of November):** if XGBoost doesn't beat persistence at h = 6 h, change the target or horizon before building more infrastructure.

## 7. MLOps loop (corrected design, see P-002)

**Why not "drift → rollback":**
- Input drift means the world changed. The *previous* model was trained on even older data, so rolling back to it rarely helps.
- Labels arrive days late, so "prediction quality" can't be measured in real time.

**The loop:**

| Signal | Detection | Action |
|---|---|---|
| Feed freshness | No messages for > 10 min, or online-feature TTL exceeded | Alert; API returns `stale: true` |
| Data quality | GE suite fails on a batch | Block the Silver/Gold write; alert; quarantine the batch |
| Input drift | Evidently daily: drift share > threshold on key features | Alert + **trigger retrain** |
| Performance regression | Matured-label MAE of `@champion` > `@previous` (or > persistence) over a 7-day window | **Automatic rollback**: move `@champion` to `@previous`; alert |
| New model | Weekly retrain → `@challenger` | Shadow-predict N days → promote only if it beats champion on matured labels |

**Rollback mechanics:**
- A rollback is an MLflow **alias move**.
- The serving layer polls the alias every N minutes and hot-reloads.
- Every prediction is logged with `model_version`, so you can always audit which model produced it.

## 8. Anti-skew proof: the parity test (defense centerpiece)

1. Replay a fixed 24 h Bronze fixture through the **streaming** path and snapshot the online features hourly.
2. Run the **batch** path on the same fixture and pull `get_historical_features` for the same timestamps.
3. Assert the two are equal within tolerance. Run this in CI on every PR.

This *demonstrates* no train–serve skew instead of just claiming it. Feast alone doesn't guarantee parity. Parity comes from the shared `features/` library plus point-in-time retrieval.

## 9. Data-quality suites (Great Expectations; pin GX 1.x, whose API differs from most tutorials)

- **Silver:**
  - Lat/lon in range
  - MMSI format valid
  - SOG ∈ [0, 50] or null
  - No duplicate keys
  - ≥ N messages/hour (feed health)
  - Max gap between messages < 30 min
- **Gold:**
  - Occupancy ≥ 0 and ≤ a plausible max
  - Arrivals − departures reconciles with the occupancy change
  - Label completeness for matured hours
- A lighter alternative for in-code checks is `pandera`.

## 10. Demo strategy

- Replay a recorded real congestion episode (e.g. a winter weather closure) at 60× speed. Show the forecast rising *before* occupancy does.
- Then trigger the loop live:
  - Inject drift by replaying with corrupted SOG units → drift alert → retrain.
  - Deploy a deliberately bad model → regression detected → rollback.
- Keep a pre-recorded video as a fallback if the live demo fails.
