"""Profile every field of captured AIS messages (Bronze NDJSON).

Usage: python collector/profile_fields.py <ndjson> [<ndjson> ...]
Prints a per-message-type, per-field profile plus reliability checks; writes data/derived/field_profile.json.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def flatten(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, f"{prefix}{k}."))
        else:
            out[f"{prefix}{k}"] = v
    return out


def summarize(values: list) -> dict:
    vals = [v.strip() if isinstance(v, str) else v for v in values]
    filled = [v for v in vals if v not in (None, "")]
    s = {"n": len(vals), "filled_pct": round(100 * len(filled) / len(vals), 1) if vals else 0,
         "distinct": len({json.dumps(v) for v in filled})}
    nums = [v for v in filled if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if nums and len(nums) == len(filled):
        q = statistics.quantiles(nums, n=20) if len(nums) > 1 else [nums[0]] * 19
        s.update(min=min(nums), p50=round(statistics.median(nums), 3), p95=round(q[18], 3), max=max(nums))
    s["top"] = Counter(json.dumps(v) for v in filled).most_common(5)
    return s


def parse_meta_time(t: str) -> datetime:
    return datetime.strptime(t[:26], "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)


def main(paths: list[Path]) -> None:
    recs = [json.loads(line) for p in paths for line in p.read_text(encoding="utf-8").splitlines()]
    recs = [r for r in recs if r["msg"].get("MessageType") != "SubscriptionConfirmation"]
    by_type: dict[str, list] = defaultdict(list)
    for r in recs:
        by_type[r["msg"]["MessageType"]].append(r)

    profile: dict = {"messages": len(recs), "by_type": {t: len(v) for t, v in by_type.items()}, "fields": {}}
    for t, rs in by_type.items():
        rows = [flatten(r["msg"]["Message"][t]) for r in rs]
        rows_meta = [flatten(r["msg"]["MetaData"], "MetaData.") for r in rs]
        keys = sorted({k for row in rows + rows_meta for k in row})
        profile["fields"][t] = {k: summarize([row.get(k) for row in rows + rows_meta if k in row]) for k in keys}

    checks: dict = {}
    pos = [r for r in by_type.get("PositionReport", [])]
    body = [r["msg"]["Message"]["PositionReport"] for r in pos]
    if body:
        n = len(body)
        checks["sentinels_pct"] = {
            "Sog=102.3 (n/a)": round(100 * sum(b["Sog"] >= 102.2 for b in body) / n, 1),
            "Cog=360 (n/a)": round(100 * sum(b["Cog"] >= 360 for b in body) / n, 1),
            "TrueHeading=511 (n/a)": round(100 * sum(b["TrueHeading"] == 511 for b in body) / n, 1),
            "RateOfTurn=-128 (n/a)": round(100 * sum(b["RateOfTurn"] == -128 for b in body) / n, 1),
            "Timestamp>=60 (n/a)": round(100 * sum(b["Timestamp"] >= 60 for b in body) / n, 1),
            "Lat 91 / Lon 181": round(100 * sum(abs(b["Latitude"]) > 90 or abs(b["Longitude"]) > 180 for b in body) / n, 1),
            "Valid=false": round(100 * sum(not b["Valid"] for b in body) / n, 1),
        }
        cross = defaultdict(Counter)
        for b in body:
            cross[b["NavigationalStatus"]]["stationary(<0.5kn)" if b["Sog"] < 0.5 else "moving"] += 1
        checks["navstatus_vs_speed"] = {str(k): dict(v) for k, v in sorted(cross.items())}
        lat = [(datetime.fromisoformat(r["received_at"]) - parse_meta_time(r["msg"]["MetaData"]["time_utc"])).total_seconds()
               for r in pos]
        checks["latency_s"] = {"p50": round(statistics.median(lat), 2), "max": round(max(lat), 2)}
        mismatch = sum(abs(r["msg"]["MetaData"]["latitude"] - b["Latitude"]) > 1e-4 for r, b in zip(pos, body))
        checks["meta_vs_body_position_mismatch"] = mismatch
        gaps = defaultdict(list)
        last: dict = {}
        for r, b in zip(pos, body):
            m, ts = r["msg"]["MetaData"]["MMSI"], parse_meta_time(r["msg"]["MetaData"]["time_utc"])
            if m in last:
                gaps["moving" if b["Sog"] >= 0.5 else "stationary"].append((ts - last[m]).total_seconds())
            last[m] = ts
        checks["report_interval_s"] = {k: {"n": len(v), "p50": round(statistics.median(v), 1)} for k, v in gaps.items() if v}
        reports = Counter(r["msg"]["MetaData"]["MMSI"] for r in pos)
        checks["class_a_vessels"] = len(reports)
        checks["reports_per_vessel_p50"] = statistics.median(reports.values())
        static_mmsi = {r["msg"]["MetaData"]["MMSI"] for r in by_type.get("ShipStaticData", [])}
        checks["class_a_with_static_pct"] = round(100 * len(set(reports) & static_mmsi) / len(reports), 1)
    st = [r["msg"]["Message"]["ShipStaticData"] for r in by_type.get("ShipStaticData", [])]
    if st:
        now = datetime.now(timezone.utc)
        eta_set = [s["Eta"] for s in st if s["Eta"].get("Month")]
        def eta_past(e):
            try:
                return datetime(now.year, e["Month"], e["Day"], tzinfo=timezone.utc) < now.replace(hour=0, minute=0)
            except ValueError:
                return True
        checks["static"] = {
            "imo_missing_pct": round(100 * sum(not s["ImoNumber"] for s in st) / len(st), 1),
            "destination_blank_pct": round(100 * sum(not s["Destination"].strip() for s in st) / len(st), 1),
            "eta_unset_pct": round(100 * (len(st) - len(eta_set)) / len(st), 1),
            "eta_in_past_pct_of_set": round(100 * sum(eta_past(e) for e in eta_set) / len(eta_set), 1) if eta_set else None,
            "draught_zero_pct": round(100 * sum(not s["MaximumStaticDraught"] for s in st) / len(st), 1),
            "type_top": Counter(s["Type"] for s in st).most_common(8),
            "length_m_p50": statistics.median(s["Dimension"]["A"] + s["Dimension"]["B"] for s in st),
        }
    profile["checks"] = checks
    out = REPO_ROOT / "data" / "derived" / "field_profile.json"
    out.write_text(json.dumps(profile, indent=1, default=str), encoding="utf-8")

    print(f"messages {profile['messages']}  {profile['by_type']}")
    for t, fields in profile["fields"].items():
        print(f"\n== {t}")
        for k, s in fields.items():
            rng = f" min={s['min']} p50={s['p50']} p95={s['p95']} max={s['max']}" if "min" in s else ""
            print(f"  {k:<40} filled={s['filled_pct']:>5}% distinct={s['distinct']:<4}{rng}  top={[x[0] for x in s['top'][:3]]}")
    print("\n== checks")
    for k, v in checks.items():
        print(f"  {k}: {v}")
    print(f"-> {out}")


if __name__ == "__main__":
    main([Path(p) for p in sys.argv[1:]])
