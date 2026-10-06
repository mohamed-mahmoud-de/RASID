# Smart Port & Maritime Congestion Predictor
### Project & Business Brief — Alexandria University Graduation Project (DE + MLOps)

**One line:** A system that predicts vessel congestion at Egypt's main maritime gateways (Port Said / Suez Canal approaches) a few hours ahead, learning from live and historical ship-movement data so operators can plan *before* the bottleneck forms instead of reacting after it.

---

## 1. The Problem

Egypt's maritime gateways are among the busiest chokepoints on earth. When too many vessels arrive at once, ships queue at anchorage waiting for a berth or a canal convoy slot. That waiting is expensive — demurrage and detention charges, wasted fuel, missed downstream logistics — and today it is mostly handled **reactively**, because operators lack a reliable forward-looking signal for when congestion is about to build.

## 2. The Solution

A prediction engine that forecasts near-term congestion — expected vessel waiting time, or a congestion index, for the Port Said / canal-approach anchorage. It learns the patterns that precede a build-up (arrival rate climbing, anchorage filling, approach speeds dropping) and predicts the next few hours.

**The decision that makes it buildable:** we derive both the model's *features* and its *ground-truth labels* directly from AIS vessel-tracking data — no proprietary port-authority data required. Using the published method (DBSCAN + convex hull to separate anchorage from berth zones, then AIS navigation status + speed + timestamps to compute waiting and turnaround times), the data is 100% real and fully obtainable by a student team.

## 3. How It Works

A two-path (batch + streaming) pipeline on a medallion (Bronze → Silver → Gold) layout, with a feature store bridging the two paths:

- **Streaming path:** live AIS → Kafka → Spark Structured Streaming computes real-time features (rolling arrival rate, vessels at anchor, mean approach speed).
- **Batch path:** historical AIS → Airflow ETL → the same feature logic → model training and scheduled retraining.
- **The bridge:** a feature store serves *identical* feature definitions to both training and live inference, so what the model learned in training matches exactly what it sees in production (no train-serve skew).
- **Serving:** a prediction API returns the congestion forecast; a dashboard visualizes it on a map.
- **Guardrails:** drift monitoring watches prediction quality and can trigger an automatic rollback to the previous model version.

## 4. Tech Stack

| Layer | Tools |
|---|---|
| Live ingestion | Python WebSocket consumer (aisstream.io) → **Apache Kafka** |
| Stream processing | **Spark Structured Streaming / PySpark** |
| Storage (medallion) | **PostgreSQL** + **Parquet**/object storage; optionally **Cassandra** for high-write raw AIS |
| Orchestration | **Apache Airflow** (batch ETL, backfill, retraining) |
| Geospatial / labeling | scikit-learn (DBSCAN), shapely / geopandas (convex hull) |
| Feature store | **Feast** — the anti-skew centerpiece |
| Model | **XGBoost** baseline; optional **LSTM** for the temporal angle |
| Tracking & registry | **MLflow** (experiments, versions, rollback) |
| Serving | **FastAPI**, containerized |
| Monitoring / drift | **Evidently AI** |
| Data quality | **Great Expectations** |
| Dashboard | **Elasticsearch + Kibana** (or Grafana / Streamlit) |
| Infra / CI-CD | **Docker / docker-compose**, **GitHub Actions** |

## 5. Data Sources

**Streaming (real):**
- **aisstream.io** — free live AIS over WebSocket, bounding-box-filtered to Port Said / the canal approach / Red Sea + Med entry. Feeds Kafka continuously.

**Batch / historical (real):**
- **Self-collected AIS** — start streaming into Bronze *now*; you accumulate genuine history over the project months. Every day of delay = lost training data.
- **Kaggle historical AIS** as backfill — *verify a dataset actually covers the Suez / Red Sea / Med region* before relying on it.
- **Open-Meteo** (free) for weather features.
- *Optional:* paid backfill (Datalastic / DataDocked, ~€80/mo) only if you need historical depth fast.

**On "simulation" — two different things, only one is fake:**
- **Replay simulator (uses REAL data):** replays your recorded AIS back into Kafka as if it were live. Value: test the pipeline anytime regardless of the live feed's uptime, reproduce a past congestion event on demand, and run a reliable live demo on defense day. This is a testing/demo tool — **real data still trains and grades the model.** Worth building.
- **Synthetic generator (fake data):** only ever used to stress-test whether the pipeline survives 10x traffic load. Never touches training — inventing ships means inventing congestion, which makes the model meaningless. Optional; skippable.

## 6. What Makes It Technically Strong

- **Feature store as the anti-skew centerpiece** — the single most defensible MLOps decision; demonstrate the same feature computed once and served to both training and inference.
- **Closed monitoring → rollback loop** — drift detected → alert → MLflow rolls back to the prior model version.
- **Data-quality gates** (Great Expectations) in the Airflow DAGs — bad AIS batches caught before they poison training.
- **Reproducible defense demo** via the replay simulator.
- **Backtesting on real events** — validate against known historical congestion (e.g. the 2021 Ever Given blockage aftermath).
- **Explainability (SHAP)** — shows *why* congestion is forecast, which real operators want.

---

## 7. Business Model

Framed as if this were a real product — which is exactly the lens a supervisor uses to test whether the project solves a real problem.

### Who it's for (target audience)

| Segment | Their pain | What the system gives them |
|---|---|---|
| **Shipping agents / freight forwarders** | Advise clients, schedule calls, avoid demurrage | Early warning to reschedule and cut waiting charges |
| **Terminal / port operators** (e.g. Suez Canal Container Terminal, DP World, APM) | Berth planning, resource/crane allocation | Forecast to allocate berths and labor proactively |
| **Shipping lines / carriers** | ETA reliability, fuel/speed planning | Slow-steam or re-sequence to avoid idle waiting |
| **Logistics & import/export companies** | Inland transport & warehouse slotting | Plan trucking and storage around realistic ETAs |
| **Port authorities / Suez Canal Authority** | Traffic management (hard to sell to as students) | Macro traffic view; likely a validation partner, not a first customer |
| **Niche: insurers, commodity traders, bunkering firms** | Congestion affects risk, prices, demand | Congestion index as a risk/pricing signal |

### The value hook (the money argument)

Demurrage and detention are large, direct costs. Even a few hours of advance warning that lets an agent or carrier re-sequence a call can avoid thousands of dollars per vessel. That is the concrete "why would anyone pay" answer: **the system's job is to convert waiting time into avoided cost.**

### Revenue models (options)

| Model | How it works | Best fit |
|---|---|---|
| **B2B SaaS subscription** | Monthly dashboard access, tiered by port/volume | Agents, operators |
| **API / usage-based** | Predictions fed into the customer's own TMS/ERP | Carriers, larger logistics firms |
| **Freemium** | Free basic congestion index; paid alerts, forecasts, API | Top-of-funnel + upsell |
| **Data-as-a-service** | Sell the cleaned AIS-derived congestion index/dataset | Traders, analysts |
| **Licensing / custom** | License to a terminal operator or authority | Enterprise / gov |

### Market & competition

Global maritime-visibility players exist (MarineTraffic/Kpler, Windward, Sinay, PortXchange, project44, FourKites) and technically cover Egyptian ports — so this is **not** an empty market. The wedge is **localization**: Egypt/Suez-tuned models, Suez convoy dynamics, Arabic interface, and a price point built for the local market rather than global enterprise contracts. Honest framing for the defense: *"no localized solution for Egyptian gateways,"* not *"no competition."*

### Cost structure

Data is largely **free** (aisstream, Open-Meteo); main costs are cloud compute and engineering time. Low variable cost per customer → healthy margins if it scaled.

### Moat / defensibility

- A **self-collected regional historical AIS dataset** that grows over time and is hard for a newcomer to replicate quickly.
- **Models tuned to local traffic and canal-convoy patterns.**
- Local relationships and lower price point than global incumbents.

### Go-to-market (realistic path)

Pilot with **one** shipping agent or terminal operator → prove avoided-cost on real calls → use that case study to expand. Land narrow, prove value, widen.

### Success metrics (how you prove it works)

- **Model:** MAE on predicted waiting time; prediction lead time (hours ahead).
- **Business:** % reduction in demurrage in a pilot; berth-utilization improvement; ETA-reliability gain.

## 8. Risks & Limitations (state these openly)

- **Single free-data dependency** — mitigated by resilient consumer + replay + Bronze persistence, and a fallback provider in mind.
- **No official port-authority data** — the AIS-derived-label approach is the answer, but real-world validation would eventually need a partner.
- **Regional feed coverage** — verify steady AIS traffic over the target zone early.
- **SAR/satellite imagery is deliberately out of scope** — high processing cost, ~6-day revisit; parked as a possible future "dark-vessel detection" feature, not a core dependency.

## 9. Team & Scope (6 people)

Five data engineers own the pipeline components (batch ETL, streaming, storage, geospatial feature engineering, orchestration). **Zane owns the MLOps domain** — feature store, model registry, serving, and the monitoring → rollback loop. Build a thin working slice end-to-end first (one port, clean pipeline), then add stretch goals (drift→rollback, SHAP, LSTM, backtesting).

---

## 10. Questions Your Supervisor Might Ask (and crisp answers)

**Where does the data come from — is it real and legal?**
Free live AIS from aisstream.io, which we're allowed to process; historical AIS self-collected plus Kaggle. No proprietary or scraped data.

**How do you get ground-truth labels without port-authority data?**
We derive congestion from AIS itself — cluster vessel positions (DBSCAN + convex hull) to identify anchorage vs berth zones, then use navigation status + speed + timestamps to compute waiting/turnaround times. This is an established published method.

**How is this different from MarineTraffic and existing tools?**
Those are global, enterprise-priced visibility platforms. Ours is prediction-focused, localized and tuned to Egyptian gateway and Suez convoy patterns, and priced for the local market.

**Who would actually pay for it?**
Shipping agents, terminal operators, and carriers — because a few hours of warning avoids demurrage/detention costs measured in thousands of dollars per vessel.

**How do you validate the model is correct?**
Holdout evaluation, backtesting against known historical congestion events, and comparing predicted vs actual waiting times.

**What's the MLOps contribution specifically?**
A feature store that eliminates train-serve skew, a model registry with versioning, and an automated drift-detection → rollback loop.

**Is it scalable to other ports?**
Yes — the same pipeline retrains per port; only the geographic bounding box and zone definitions change.

**What if the live feed goes down?**
Resilient consumer (auto-reconnect + backoff), data persisted to Bronze so gaps are small, and the replay simulator covers testing and demos.

**Is the scope realistic for six people and the timeline?**
Yes — components are cleanly divided, and we deliver a working thin slice before attempting stretch goals.

**What's the novel contribution?**
A localized, AIS-only congestion-prediction system for Egyptian maritime gateways, delivered with production-grade MLOps — combining a real Egyptian problem with a modern, defensible data + ML pipeline.
