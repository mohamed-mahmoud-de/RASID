# Project Context & Background

## 1. The domain in plain terms

**Egypt's gateways.** Port Said sits at the northern (Mediterranean) entrance of the Suez Canal. It includes East Port Said (Suez Canal Container Terminal), West Port Said, and the anchorage areas north of the canal entrance. The other Egyptian gateways are Alexandria/Dekheila, Damietta, and Sokhna.
- **MVP scope:** the Port Said / northern canal-approach anchorage.
- **Collect wider than we model.** The live bounding box should also cover Alexandria and Damietta (see `data-and-mlops.md`).

**How the canal works.** The Suez Canal Authority (SCA) runs a convoy system. Vessels wait at anchorage until they are assigned to a convoy.
- At the canal, waiting is driven by convoy scheduling and capacity, not by berth availability. At the port terminals, waiting *is* driven by berth availability.
- These are two different queues, and they need different label definitions (see decision O-001).
- **Confirm the current SCA convoy schedule and cut-off rules** from SCA's published Rules of Navigation before modeling. Don't assume them.

**Why waiting costs money.** Under charter parties, laytime is the time allowed for loading or discharge. After laytime is exhausted, the charterer pays **demurrage** to the owner per day. **Detention** charges apply to containers held too long. Waiting also burns fuel and breaks downstream plans: trucking, warehouse slots, and the connecting vessel. That is the value hook: **convert waiting time into avoided cost.**
- *Any per-day dollar figure used in the deck or thesis must be cited*, e.g. from a broker/charter-rate report.

## 2. The 2026 situation (important for modeling and pitch)

- **Background:** from late 2023, Houthi attacks in the Red Sea diverted most container lines around the Cape of Good Hope. Suez transits collapsed.
- **2026 recovery:** a gradual, service-by-service return.
  - Maersk, MSC, CMA CGM, Hapag-Lloyd, and COSCO have moved selected loops back.
  - Maersk resumed the ME11 service via Suez in mid-February 2026.
  - Trade press reports August 2026 at 1,358 transits (+27% YoY) and USD 567.1 M revenue (+56.7% YoY). The baseline **is consistent with official SCA data**: the SCA 2025 annual report gives Aug 2025 = 1,070 vessels, and 2025 months ranged 864–1,160 (≈28–39/day).
  - **But the two series disagree:** IMF PortWatch (pulled 2026-10-06) shows a flat ~40–43/day from Oct 2025 to Sep 2026. In Oct 2025 PortWatch says ≈41/day while SCA says ≈36/day; in Aug 2026 PortWatch says ≈41/day while SCA says ≈44/day.
  - Methodologies differ: PortWatch is AIS-derived, while SCA counts official transits. **Cite SCA for official totals; use PortWatch only for daily resolution, and always label which source you use.** The source disagreement is itself a validation finding worth reporting in the thesis.
  - Returns are conditional on security. The corridor is still a listed war-risk area, and carriers keep Cape contingencies.
- **Implications:**
  1. **Non-stationarity is guaranteed.** The traffic regime is shifting *during* our collection window. This is a gift for the MLOps story: drift monitoring and retraining become necessary, not decorative. It is also a risk: report metrics per regime.
  2. **Timeliness.** A lumpy return of traffic (bunching, schedule recovery) is exactly when congestion forecasting matters. This strengthens the pitch.
  3. **Volume.** About 41 transits/day (PortWatch, 2026) is fewer vessels than pre-crisis, so expect smaller samples per hour. Size the models accordingly. Local reference data is in `data/reference/portwatch_*.json`.

## 3. Glossary

| Term | Meaning |
|---|---|
| AIS | Automatic Identification System. VHF broadcasts of vessel position/identity, received by terrestrial stations and satellites |
| MMSI | 9-digit vessel radio ID. The primary key in AIS. Can be reused or spoofed |
| IMO number | Permanent hull ID (7 digits). Arrives in static messages (type 5) |
| NavStatus | Crew-set status: 0 under way (engine), 1 at anchor, 5 moored, 15 undefined. **Often stale — never trust it alone** |
| SOG / COG / Heading | Speed over ground (kn) / course over ground / true heading. Sentinel values: SOG 102.3, COG 360, heading 511 = not available |
| Lat 91 / Lon 181 | AIS sentinel for "position not available" |
| Anchorage | Sea area where vessels wait at anchor |
| Berth | Quay position where cargo is handled |
| Convoy | SCA-scheduled group transit through the canal |
| Waiting time | Time from anchoring to leaving the anchorage toward service (canal entry or berth) |
| Turnaround time | Port arrival → port departure |
| Demurrage / detention | Charges for exceeding laytime (vessel) / free time (containers) |
| Medallion | Bronze (raw) → Silver (clean, conformed) → Gold (aggregated, model-ready) |
| Train–serve skew | Features computed differently in training vs. production, which silently degrades a model |
| Point-in-time join | Building training rows using only data available *as of* each timestamp, so there is no leakage |

## 4. Literature (verified 2026-10-06)

| Reference | What it gives us | Status |
|---|---|---|
| Peng, W., Bai, X., Yang, D., Yuen, K. F., & Wu, J. (2023). A deep learning approach for port congestion estimation and prediction. *Maritime Policy & Management*, 50(7), 835–860. | **Core method.** AIS from 3,957 container ships (Mar–Apr 2017), top-20 ports. DBSCAN + convex hull find berth/anchorage areas. Hourly congestion measures from traffic volume and turnaround time. LSTM prediction. **Adding congestion-propagation features (from other ports) improved predictions**, so we should borrow that idea. | ✅ Verified. Proposal had wrong initial/year |
| Chico, C., Cordel, M. O. II, Mariasingham, M. J., & Tan, E. S. (2025). Analyzing anomalous events in passageways with high-frequency ship signals. *PLOS ONE*. doi:10.1371/journal.pone.0320129 | AIS-only zone framework for Suez: **North Anchorage (Port Said)**, Great Bitter Lake, South Anchorage (Suez). Vessels count as "queued" above the 95th-percentile dwell time of the business-as-usual period, and as transiting if seen in ≥2 zones. Data: Spire via UN Global Platform. Studies the 2021 blockage, Bosporus 2022, Bab el-Mandeb 2023. | ✅ Verified. Proposal mislabels the Port Said zone |
| Budiman, J. (2024). Machine-Learning based Ship Traffic Prediction in the Suez Canal. M.Eng. thesis, MIT. | Annual average daily traffic (AADT) prediction from AIS + satellite imagery. A different target. | ⚠ Not yet verified |
| Mostafa, M. M. Forecasting the Suez Canal traffic: a neural network analysis. | ARIMA/NN tonnage forecasting (macro level). | ⚠ Year/venue missing; verify |

Reading to add (search before citing): AIS-based port-call detection, ETA/waiting-time prediction (e.g. survival models), conformal prediction for time series.

## 5. Competitive landscape (from proposal)

- **Global platforms** (cover Egypt, but generic): MarineTraffic/Kpler, Windward, Sinay, project44, FourKites, GoComet (has a port-congestion dashboard), PortXchange.
- **Free public monitors:** World Monitor (Suez chokepoint severity), IMF PortWatch (daily transit/port-call counts since 2019).
- **Open source:** `gabrielfuenmar/suez-canal-transits` (transit extraction, no ML), `yossef1222/suez-blockage-analytics` (synthetic data).
- **Honest positioning:** "no localized, production-grade *predictive* system for Egyptian gateways", **not** "no competition". Congestion *dashboards* are commoditized. The wedge is localized forecasts plus decisions delivered in the customer's workflow (see `strategy.md`).

## 6. Source material in this folder

- `congestion-predictor-brief.md` — project & business brief (Sep 16, 2026)
- `Smart-Port-Congestion-Predictor-Proposal.docx` — formal 15-section proposal (Sep 18, 2026)
- `Smart-Port-and-Maritime-Congestion-Predictor.pdf` — 10-slide Gamma deck (Sep 18, 2026). Remove the "Made with Gamma" badge for the defense version.
