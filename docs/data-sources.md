# Data Sources — Port Said / Suez Canal Congestion

Research date: 2026-10-06. Focus: Port Said and the Suez Canal. Alexandria appears only as a supplementary feature.

**Verification legend:**
- ✅ **tested by us**: live query or primary data inspected
- ☑️ **provider documentation**: not yet tested by us
- ❓ **unverified**: needs confirmation

**Relevance:** ★★★ directly measures waiting or queues · ★★ throughput / validation · ★ supplementary

## Bottom line

1. **No free real-time source covers Port Said or the Suez Canal.** All three free live AIS networks were tested, and none hears Egyptian waters.
2. **The best free source is Global Fishing Watch** (satellite AIS). It provides hourly per-ship presence and port-visit events from 2012 to about 3–4 days ago, which is enough to measure queues and waiting times historically.
3. **Official totals come from the Suez Canal Authority** (monthly) and the **SCA daily bulletins in the press**. **Daily AIS-derived counts come from IMF PortWatch.**
4. **Real-time forecasting at Port Said requires a paid satellite-AIS feed** (Spire, MarineTraffic/Kpler, Datalastic, Voyage Radar, …).

## Tier 1 — Core sources (free)

| # | Source (type) | What it provides | Access | Cost | Real-time? | Limitations | Congestion relevance |
|---|---|---|---|---|---|---|---|
| 1 | **Global Fishing Watch: AIS Vessel Presence** (satellite + terrestrial AIS) ☑️ | One position per vessel per hour, gridded at **0.01° (~1 km)**. Group by **MMSI**, filter by vessel type (CARGO, BUNKER_OR_TANKER, …) and speed band (**<2 kn = stationary**). Coverage 2012 → present | 4Wings API (CSV/JSON); Python and R clients; free API token (**must be requested on behalf of an organization**, with an org email) | **Free**, CC BY-NC 4.0: non-commercial only, attribution "Powered by Global Fishing Watch"; 50k requests/day, 1.5M/month | ❌ ~3–5 days delay. **API docs say 2017 → ~5 days ago; the platform announcement says 2012 → 96 h. Verify with a token** | Gridded rather than raw tracks; 1 fix/hour; satellite may miss ships in dense anchorages; no commercial license available publicly | ★★★ **Queue length** (stationary cargo/tankers in the Port Said anchorage per hour) and **per-ship waiting duration** |
| 2 | **Global Fishing Watch: Port Visits** (Events API) ☑️ | Port entry / stop / gap / exit events for **all vessel types**, 2012 →, confidence levels 1–4 | Events API, same token | **Free** (non-commercial) | ❌ ~72 h | Port visit ≠ canal transit; port boundaries are GFW's definition | ★★★ **Arrival and departure times** at Port Said → time in port, arrival rate |
| 3 | **Global Fishing Watch: Anchorages dataset** ☑️ | ~160,000 anchorage points (S2 level-14 cells, ~0.5 km) grouped into ~32,000 named ports, derived from stationary AIS since 2012 | Download (free registration) | **Free** | Static | Generic definitions; still needs a map review | ★★ Ready-made **Port Said anchorage zones**, to validate or replace our DBSCAN zones |
| 4 | **IMF PortWatch** (AIS-derived statistics) ✅ | **Daily Suez Canal transits** by type (container, tanker, dry bulk, general cargo, Ro-Ro) and capacity since 2019; daily **port calls** for Port Said and Damietta | ArcGIS REST, no key (`collector/fetch_portwatch.py`); CSV export | **Free** | ❌ ~2–4 days | Counts, not waits; **trend disagrees with SCA** (see project-context.md) | ★★ Throughput, daily validation of our counts, regime context |
| 5 | **Suez Canal Authority: official statistics** ✅ | Annual reports (PDF): totals and daily averages **1975–2025**, **monthly** vessels and net tonnage, by ship type, cargo by direction. News pages with traffic announcements | suezcanal.gov.eg (PDF downloads, news) | **Free** | ❌ Monthly/annual; announcements irregular | **No waiting-time or queue data**; PDFs need parsing | ★★ **Authoritative totals**; monthly validation; ground truth for major events |
| 6 | **SCA daily bulletins via Egyptian press** (Al-Ahram Gate, etc.) ✅ | Daily transits in both directions + net tonnage, often broken down by vessel type ("عبور 65 سفينة من الاتجاهين…") | News sites (scraping/RSS) | **Free** | ⚠️ Daily, same day | Not every day; Arabic text parsing; respect site terms | ★★ **Highest-frequency official number**; event annotations (records, closures, weather) |

## Tier 2 — Real-time AIS (would enable live forecasting); mostly paid

| # | Source (type) | What it provides | Access | Cost | Real-time? | Limitations | Congestion relevance |
|---|---|---|---|---|---|---|---|
| 7 | **Spire Maritime** (satellite + terrestrial AIS) ☑️ | Global live and historical AIS, including Suez. Spire is the data behind the UN Global Platform used in the PLOS 2025 Suez study | API/streaming via sales | **Paid** (enterprise) | ✅ | Cost; ask about research access | ★★★ Live queue and waits |
| 8 | **MarineTraffic / Kpler** (AIS + analytics) ☑️ | Live/historical AIS, port calls, congestion analytics, 15+ years of history | Subscription/API; **Academic Relations team** on request | **Paid**; academic access on request | ✅ | Cost; academic access not guaranteed | ★★★ |
| 9 | **Datalastic** (AIS API) ☑️ | Live positions, "area traffic scan", historical positions | REST | **Paid** (credit plans; 14-day money-back) | ⚠️ Poll (near-real-time) | REST only | ★★★ |
| 10 | **Voyage Radar** (terrestrial + satellite AIS) ☑️ | Live AIS; states Suez coverage | REST | 500 free credits (one-time); then $39–949/mo | ✅ | Free tier is a one-off | ★★ |
| 11 | **VesselAPI / VesselFinder API / Vessels API** ☑️ | Live positions, bounding-box queries | REST | 150 calls/month free / trial credits / 7-day trial | ✅ | Free tiers far too small for continuous use; VesselAPI is terrestrial-only (satellite is a paid add-on) | ★★ |
| 12 | **Sinay Port Congestion API** (analytics) ☑️ | Hourly congestion as a percentage of port capacity, and versus average | REST | 100 calls/month free; paid beyond | ⚠️ Hourly | **Port area excludes waiting zones**, so it doesn't measure the anchorage queue; Port Said coverage ❓ | ★ |

### Cheapest live options (checked 2026-10-06)

For 6–12 h forecasts **one snapshot of the Port Said box per hour is enough**: ~720 requests/month, or 1,440 at 30-minute intervals. So a small area-query plan is sufficient.

| Option | Price | Quota | Enough for hourly snapshots? | Sees Port Said live? |
|---|---|---|---|---|
| **GDELT Cloud: Academic & Research** ☑️ | **Free** (verification) | 5,000 units/month | Likely | ❓ terrestrial-only AIS, data since June 2026. **Test** |
| **VesselAPI: Free** ☑️ | Free, no card | 150 calls/month | No (≈6 days of hourly) | ❓ terrestrial-only. **Test** |
| **Voyage Radar: Free** ☑️ | Free, one-time | 500 credits | No (one-off) | ☑️ claims Suez coverage (terrestrial + satellite). **Test** |
| **VesselAPI: Basic** ☑️ | **$14.99/mo** | 1,500 calls | Yes, if a snapshot fits in ≤2 pages (bbox results are paginated) | ❓ |
| **Voyage Radar: Buoy** ☑️ | $39/mo | 10,000 credits | Likely (credits per area query unknown) | ☑️ |
| VesselAPI: Starter | $59.99/mo | 15,000 calls | Yes, even every 5–10 min | ❓ |
| Datalastic: Starter | price not shown (team est. ~€80) | 20,000 credits | Yes | ❓ |

Rules:
- **Test free tiers first**, and pay only for a provider that demonstrably sees Port Said ships.
- One account per provider. Don't multiply free accounts.
- Free one-time credits can be **saved for a 2–3 week live demo window** before the defense.

## Tier 3 — Satellite imagery (independent of AIS)

| # | Source | What it provides | Access | Cost | Real-time? | Limitations | Relevance |
|---|---|---|---|---|---|---|---|
| 13 | **GFW SAR vessel detections** (Sentinel-1 radar) ☑️ | Detected vessels, **including ships with AIS off** | 4Wings API | **Free** (non-commercial) | ❌ Every few days + processing delay | Sparse revisits; no identity for "dark" ships | ★ Independent check of anchorage counts |
| 14 | **Copernicus Sentinel-1 / Sentinel-2** ☑️ | Radar and optical imagery | Copernicus Data Space Ecosystem (free account) | **Free** | ❌ Revisit every several days | Need our own ship detection; clouds (S2) | ★ Case studies, validation |
| 15 | **Planet Education & Research (Basic)** ☑️ | PlanetScope ~3 m imagery | Application with a university email | **Free**: 3,000 km²/month, **30-day delay** | ❌ | Quota, delay, non-commercial | ★ Visual verification of queues on key dates |

## Tier 4 — Free on application or request (not guaranteed)

| # | Source | What it provides | Access | Relevance |
|---|---|---|---|---|
| 16 | **UN Global Platform AIS** ❓ | Spire AIS for official statistics/research; used by Chico et al. (2025) for Suez | Partnership/application (via university / CAPMAS?) | ★★★ if granted |
| 17 | **Leth Agencies** (Suez Canal agent) ☑️ | Newsletters and disruption updates, e.g. vessels at anchor at **Port Said / Great Bitter Lake / Suez** | Website newsletters; contact for detailed reports | ★★ Ground truth for queue length during disruptions |
| 18 | **Academic authors** (Chico et al. 2025, PLOS ONE; Peng et al. 2023) ❓ | Processed Suez dwell/queue series | Email request | ★★ Benchmarks |

## Tier 5 — Supplementary features

| # | Source | Provides | Cost | Real-time? | Use |
|---|---|---|---|---|---|
| 19 | **Open-Meteo** (forecast + marine API) ✅ docs | Wind, gusts, wave height | Free (non-commercial) | ✅ | Weather-driven delays/closures |
| 20 | **Copernicus Marine Service** ☑️ | Waves, currents | Free (registration) | Daily | Sea-state features |
| 21 | **GDELT** ☑️ | Global news events, updated every 15 min | Free | ✅ | Disruption flags (security, accidents, strikes); noisy |
| 22 | **Alexandria Port Authority live board** (supplementary only) ✅ | Expected / in-port / departed ships with arrival, berthing and departure times, cargo, origin/destination | Free, public web page (no API; ask permission) | ✅ | Regional spillover feature; ships declaring Port Said as origin/destination; pipeline testbed |
| 23 | **Damietta port daily bulletins** (press) ✅ | Ships in port, arrivals, departures, cargo | Free | Daily | Regional context |
| 24 | **Alexandria storm calendar (كشف النوات)** ✅ | Seasonal winter-storm schedule | Free | Seasonal | Weather-closure flags (Alexandria-centric) |

## Tested and rejected

| Source | Why |
|---|---|
| aisstream.io ✅ | 0 vessels at Port Said or in the canal over a 10-minute live test; receivers in Turkey, Cyprus, Israel |
| Open Waters AIS ✅ | Free and anonymous (aisstream + AISHub + volunteers), but live ships in the Egypt box were only off Israel; El Arish/Port Said sightings were 56–65 h old |
| AISHub ☑️ | Requires contributing your own antenna; no Egyptian stations evident |
| World Monitor ☑️ | Derivative (PortWatch + aisstream), so it inherits the same gaps |
| Kaggle / Zenodo ✅ search | No Suez / Port Said AIS dataset found |

## Recommended stack (free-only constraint)

- **Batch / history (core):**
  - GFW presence + port visits + anchorages → hourly queue length, per-ship waits, arrivals/departures (2012 →, including the 2021 Ever Given event)
  - PortWatch → daily validation
  - SCA → official monthly totals
- **Streaming:** no free live source exists, so stream what is available:
  - (a) daily ingestion of the newest GFW data (3–4 days late) into Kafka
  - (b) replay simulator for the live demo
  - (c) live supplementary streams: Open-Meteo, GDELT, SCA daily bulletins, and optionally the Alexandria board
- **Validation:** SCA monthly totals; PortWatch daily; GFW SAR / Sentinel spot checks; Leth queue counts during disruptions.
- **If a budget appears later:** one paid satellite-AIS feed (Spire / MarineTraffic-Kpler / Datalastic) enables true real-time Port Said forecasting with no pipeline changes, because it's just a new collector adapter.
