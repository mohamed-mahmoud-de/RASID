# Rasid — Project Documents

Documents for supervisor review (Prof. Mohamed Kholief). Code is kept out of the repository until the documents are approved (decision D-009).

## Suggested reading order

| # | Document | What it covers |
|---|---|---|
| 1 | [proposal/](proposal/) | Original submission: proposal (.docx), project brief (.md), presentation deck (.pdf) |
| 2 | [maritime-101.md](maritime-101.md) | Plain-English guide to every shipping term used in the project |
| 3 | [decision-log.md](decision-log.md) | All decisions (incl. **D-008: data sources**), test results, open questions |
| 4 | [data-sources.md](data-sources.md) | Catalog of every Port Said / Suez data source we evaluated: free vs. paid, live vs. historical, tested vs. documented |
| 5 | [reports/gfw-validation.md](reports/gfw-validation.md) | Evidence for the main data source: Port Said coverage, data latency, and the **Ever Given 2021** test |
| 6 | [reports/data_quality_report.md](reports/data_quality_report.md) | Data-quality analysis of the Alexandria Port Authority board and IMF PortWatch (profiling, checks, corrections, comparison) |
| 7 | [architecture.md](architecture.md) | System design: data flow, components, storage layers, API contract |
| 8 | [data-and-mlops.md](data-and-mlops.md) | Cleaning rules, labels, features, models, evaluation, MLOps loop |
| 9 | [roadmap.md](roadmap.md) | Phases, milestones, workstreams, task checklists |
| 10 | [project-context.md](project-context.md) | Domain background, 2026 Suez situation, literature (verified citations), competitors |
| 11 | [strategy.md](strategy.md) | Commercialization and startup path |
| 12 | [meeting-notes.md](meeting-notes.md) | Meeting and customer-interview templates |

## Status in one paragraph (2026-10-07)

- **Live AIS:** no free live feed covers Egyptian waters (tested). The project therefore uses free sources only (decision D-008).
- **Port Said / Suez Canal (main analysis):** Global Fishing Watch satellite AIS, hourly per ship, 2017 to ~5 days ago. It's used to train and backtest 6–12 h congestion forecasts. It captured the 2021 Ever Given queue (≈15 → 160 waiting ships).
- **Alexandria (live showcase):** the Alexandria Port Authority public ship board, collected every 30 minutes and combined with GFW history after a 4–6 week overlap.
- **Validation:** IMF PortWatch and Suez Canal Authority statistics.
