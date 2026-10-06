# Rasid (راصد) — Smart Port & Maritime Congestion Predictor

Forecasting vessel congestion at Egypt's maritime gateways (Port Said / Suez Canal) **6–12 hours ahead**, using ship-tracking (AIS) data and a production-grade data engineering + MLOps pipeline.

Graduation project, **Faculty of Science, SIM Department, Alexandria University**. Supervisor: **Prof. Mohamed Kholief**.

**Team:**
- Mohamed Mahmoud (Team Leader, Data Engineer & MLOps)
- Youssef Nasser
- Youssef Elkomy
- Alhassan Mohamed
- Reem Adel

## 📄 Documents

**All project documents are in [`docs/`](docs/README.md)**, with a suggested reading order.

New to shipping terms? Start with [`docs/maritime-101.md`](docs/maritime-101.md).

## Status (2026-10-07)

- **Data plan decided (D-008, free sources only):**
  - **Port Said / Suez:** Global Fishing Watch satellite AIS for training and backtesting ([validation](docs/reports/gfw-validation.md), incl. the Ever Given 2021 test).
  - **Alexandria:** the Port Authority's live ship board for live predictions.
  - **Validation:** IMF PortWatch and Suez Canal Authority statistics.
- This repository currently contains **documents only**, for supervisor review. Source code will be added after the documents are approved.

---
*Port Said / Suez data powered by [Global Fishing Watch](https://globalfishingwatch.org) (CC BY-NC 4.0, non-commercial use).*
