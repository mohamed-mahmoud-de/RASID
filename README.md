# Rasid (راصد) — Smart Port & Maritime Congestion Predictor

Predicting how long ships will wait at Egypt's maritime gateways (Port Said / Suez Canal approach), 6–24 hours ahead, using live ship-tracking (AIS) data and a production-grade data + MLOps pipeline.

Graduation project, **Faculty of Science, SIM Department, Alexandria University**. Supervisor: **Prof. Mohamed Kholief**.

**Team:**
- Mohamed Mahmoud (Team Leader, Data Engineer & MLOps)
- Youssef Nasser
- Youssef Elkomy
- Alhassan Mohamed
- Reem Adel

## New to shipping? Start here

👉 [`claude/maritime-101.md`](claude/maritime-101.md) explains every shipping term (AIS, ETA, anchorage, demurrage…) in plain English.

## Docs

| File | What's in it |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Project summary, current status, conventions, known issues. Also read automatically by Claude Code |
| [`claude/project-context.md`](claude/project-context.md) | Background, literature, competitors |
| [`claude/architecture.md`](claude/architecture.md) | System design, data flow, API contract, repo layout |
| [`claude/data-and-mlops.md`](claude/data-and-mlops.md) | Data sources, cleaning rules, labels, features, models, MLOps loop |
| [`claude/roadmap.md`](claude/roadmap.md) | Phases, milestones, task checklists |
| [`claude/decision-log.md`](claude/decision-log.md) | Decisions made / proposed / open, and test results |
| [`claude/strategy.md`](claude/strategy.md) | Commercialization and startup strategy |
| [`claude/meeting-notes.md`](claude/meeting-notes.md) | Meeting and customer-interview templates |

## Current status (2026-10-06)

- Proposal, brief, and deck are done (in the repo root).
- First live data test done. **Finding: the free AIS feed (aisstream.io) has ~0% coverage of Egyptian waters.** It saw no ships at Port Said or in the canal, while IMF PortWatch reports ~40 canal transits/day.
- The data-source decision (own antenna vs. paid feed vs. starting with Alexandria) is open. See decision **O-007** in [`claude/decision-log.md`](claude/decision-log.md).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then paste your own key from https://aisstream.io

python collector/capture_sample.py --minutes 10       # live AIS -> data/bronze/sample/
python collector/summarize_sample.py data/bronze/sample/date=*/ais_*.ndjson
python collector/profile_fields.py data/bronze/sample/date=*/ais_*.ndjson
python collector/fetch_portwatch.py                   # IMF PortWatch reference data -> data/reference/
```

`.env` (API keys) and `data/` (captured data) are **gitignored**. Never commit them. Each teammate uses their own aisstream key, and the free tier allows 3 connections per account.
