# Strategy: From Graduation Project to Product

Everything here is a hypothesis to validate with customers. None of it is established fact. Pricing numbers are placeholders until interviews say otherwise.

## 1. Commercialization path

**Sell decisions, not dashboards.**
- Congestion dashboards are commoditized: MarineTraffic/Kpler, GoComet, and free monitors like World Monitor and IMF PortWatch already exist.
- What isn't commoditized is an answer like: *"Your vessel arriving Thursday has a 70% chance of waiting > 24 h at Port Said. Here's why."*
- Delivered in Arabic and English, through the channel the customer already uses.

**Staged offer:**
1. **Free:** a public weekly *Egypt Gateway Congestion Index* (LinkedIn/newsletter/web). It builds an audience, credibility, and leads at zero marginal cost.
2. **Rasid Alerts (SaaS):** the customer uploads their vessel list or bookings. They get wait-risk forecasts and threshold alerts via email/WhatsApp, plus a dashboard. Target: shipping agents and freight forwarders (many SMEs in Alexandria/Port Said).
3. **Rasid API:** forecasts and congestion index via REST/webhooks for carriers, terminals, logistics platforms, and TMS/ERP vendors. Usage- or tier-priced.
4. **Data products:** a historical congestion index and wait-time dataset for traders, insurers, analysts, and banks.

**Niche wedges worth testing early:**
- **Bunker suppliers and ship chandlers at Port Said.** Anchorage occupancy is *their demand forecast*. Port Said is a bunkering hub. This could be an easier first sale than terminals.
- **Freight forwarders.** Use realistic ETAs to plan trucking and warehouse slots.

**Prerequisites before charging money** (blocking):
- **AIS data rights.** aisstream.io offers no SLA, no durable replay, and no published commercial license. Options:
  - (a) a licensed feed (Spire, ORBCOMM, MarineTraffic/Kpler API, Datalastic, etc.), with a region-only license to control cost;
  - (b) **our own terrestrial AIS receivers** at Port Said/Alexandria/Damietta (low-cost hardware). Better local coverage, a proprietary stream, and data-exchange rights with aggregators such as AISHub. Check Egyptian (NTRA) rules for receive-only radio equipment first.
- **Weather:** Open-Meteo requires a paid plan for commercial use.
- **COGS:** AIS licensing becomes the main cost of goods. Model it before setting prices.

## 2. Enterprise adoption: what makes companies buy

| Need | What we build |
|---|---|
| Trust | A public **live accuracy page** (rolling MAE, interval coverage, vs. baselines). Model cards. SHAP drivers in plain language |
| Risk framing | Probabilistic forecasts (P10/P50/P90, probability wait > X h), not single numbers |
| Workflow fit | Alerts on *their* vessels; WhatsApp/email; Excel export; REST + webhooks; Power BI connector later |
| ROI proof | An ROI calculator fed by their own past calls: "these 12 calls would have saved $X in demurrage" |
| Integration | API keys, SLAs, versioned API. Later: integration with Egypt's trade single window ecosystem (Nafeza) and port community systems |
| Security | SSO, RBAC, audit logs, data residency options, documented security practices (SOC 2-style controls as you grow) |
| Language | Arabic-first UI and reports, a differentiator vs. global incumbents |
| Pilot structure | 8–12 weeks, one success metric agreed upfront, **their actual anchorage/berth timestamps shared** (this also validates our labels) |

**Validation partners (not first customers):** the Suez Canal Authority, the Maritime Transport Sector, and port authorities. Pursue them for data and credibility, not revenue. Sales cycles there are long.

## 3. Startup potential: what it would take

**What's genuinely strong:**
- A real, costly, local problem.
- A team that can actually build data infrastructure.
- A dataset that compounds daily and that a newcomer can't backfill for free.
- An Arabic-first, locally priced wedge that global players won't bother with.

**What's missing (be honest):**
1. **Commercial/domain founder or advisor.** Five data engineers and no one who has sold to, or worked in, shipping. Recruit a maritime advisor: an ex-shipping agent, port-ops professional, or someone from Alexandria's Arab Academy for Science, Technology & Maritime Transport (AASTMT).
2. **Customer evidence:** 20 discovery interviews, then 2–3 pilots, then 1 paying customer. That sequence matters more than any feature.
3. **Data rights** (see §1).
4. **Legal hygiene:**
   - **Clarify Alexandria University's IP policy for graduation projects** before incorporating.
   - Sign a founders' agreement with vesting and roles.
   - Decide who is in. Not all five need to be founders.
5. **Funding route** (verify current cycles):
   - ITIDA/TIEC programs, Flat6Labs, Falak Startups, AUC Venture Lab, ASRT grants
   - maritime-specific accelerators such as PortXL
   - Use university competitions and demo days for visibility

**Kill / pivot criteria** (set them now):
- If no segment will pay after ~20 interviews, or the model can't beat persistence/convoy baselines meaningfully, then pivot to a data product, analytics consulting, or a different maritime problem. Use the same pipeline.

**Expansion logic:** all Egyptian gateways → Red Sea / East Med ports (Saudi Red Sea ports, Aqaba, …) → MENA. Arabic-first and regionally priced throughout. The pipeline is already parameterized by bbox + zone set.

## 4. Technical roadmap to production quality

| Level | Adds |
|---|---|
| **Academic MVP** (Jun 2027) | One gateway, batch + streaming, Feast parity, MLflow loop, quantile XGBoost, SHAP, replay demo |
| **Pilot-grade** (+3–6 months) | Licensed or own-receiver AIS; all Egyptian gateways (Alexandria, Dekheila, Damietta, East/West Port Said, Sokhna); per-vessel wait/ETA predictions; alerting; API keys + rate limits; backups; uptime monitoring; accuracy page |
| **Production SaaS** (+6–12 months) | Multi-tenant auth (SSO/RBAC); cloud deployment with IaC (Terraform); managed Kafka/Postgres/object storage; observability (Prometheus, Grafana, OpenTelemetry, on-call alerts); data contracts + schema registry; DR plan; cost monitoring; model cards + data cards; a global model with per-port fine-tuning for cold-start ports |
| **Differentiators** | Arabic natural-language daily briefings, generated by an LLM grounded strictly in forecast data; what-if scenarios ("if 15 more vessels arrive…"); survival-model per-vessel waits; congestion propagation across the Med/Red Sea network |

**Engineering principle:** don't add Kubernetes until a single VM + compose actually hurts. At single-region scale, revisit whether Spark streaming is worth its cost vs. a lighter stream processor. Keep Spark for the thesis.

## 5. Team & process

**Cadence** (Sun–Thu week):
- **Sunday:** 45-min sync. Review the board, check blockers, decide.
- **Daily:** async standup thread (yesterday / today / blockers).
- **Biweekly:** demo + a 1-page written update to Prof. Kholief.
- **Monthly:** retrospective.

**Tools:**
- GitHub: private monorepo, Issues, Projects board, Actions
- One chat channel (Discord/Slack/WhatsApp) with a `#alerts` channel for pipeline alerts
- The shared always-on VM
- MLflow as the experiment notebook
- `CLAUDE.md` + `claude/` as the source of truth, used with Claude Code

**Engineering practices:**
- Trunk-based development: short-lived branches, PR + 1 review, Conventional Commits.
- CI gates: ruff, pytest, docker build, **parity test**.
- **Data contracts:** pydantic schemas for Kafka messages and Gold tables. Breaking changes need a decision-log entry.
- Reproducibility: pinned dependencies, a `Makefile` (`make up`, `make test`, `make replay`), and a small checked-in replay fixture.
- Definition of done: code + tests + docs + demoable.

**People practices:**
- Every workstream has a primary *and* a backup. Pair once a week across workstreams.
- **Write the thesis continuously.** Each workstream drafts its chapter as it builds. Don't leave writing to May.
- The business track rotates, so everyone hears customers firsthand at least twice.
