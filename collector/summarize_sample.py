"""Summarize a raw AIS capture (Bronze NDJSON) into stats + per-vessel snapshot.

Usage:
    python collector/summarize_sample.py data/bronze/sample/date=.../ais_*.ndjson

Writes data/derived/sample_summary.json and prints the headline numbers.
Region labels are rough lat/lon boxes for exploration only - real zones come from DBSCAN.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POSITION_TYPES = {"PositionReport", "StandardClassBPositionReport", "ExtendedClassBPositionReport"}
NAV_STATUS = {0: "under way (engine)", 1: "at anchor", 2: "not under command", 3: "restricted manoeuvrability",
              5: "moored", 7: "fishing", 8: "under way (sailing)", 15: "undefined"}


def ship_category(code: int | None) -> str:
    if code is None or code == 0:
        return "unknown"
    if 70 <= code <= 79:
        return "cargo"
    if 80 <= code <= 89:
        return "tanker"
    if 60 <= code <= 69:
        return "passenger"
    if code in (31, 32, 52, 50, 53, 51, 54, 55):
        return "tug / pilot / service"
    if code == 30:
        return "fishing"
    return "other"


def region(lat: float, lon: float) -> str:
    if not (29.5 <= lat <= 33.5 and 29.5 <= lon <= 34.5):
        return "outside Egypt box"
    if lon >= 34.2 and lat >= 31.2:
        return "Israel coast"
    if lon < 30.6:
        return "Alexandria"
    if lon < 32.0 and lat > 31.2:
        return "Damietta"
    if lat >= 31.2 and 32.0 <= lon <= 32.7:
        return "Port Said approach"
    if 30.05 <= lat < 31.2 and 32.15 <= lon <= 32.65:
        return "Suez Canal"
    if lat < 30.05:
        return "Suez / Gulf of Suez"
    return "Open Med"


def main(path: Path) -> None:
    counts: Counter[str] = Counter()
    times: list[str] = []
    per_minute: Counter[str] = Counter()
    latest: dict[int, dict] = {}
    static: dict[int, dict] = {}
    reports_per_vessel: Counter[int] = Counter()
    track: dict[int, list] = defaultdict(list)
    quality = Counter()
    samples: dict[str, dict] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        msg = rec["msg"]
        mtype = msg.get("MessageType", "?")
        counts[mtype] += 1
        samples.setdefault(mtype, msg)
        per_minute[rec["received_at"][:16]] += 1
        times.append(rec["received_at"])
        meta = msg.get("MetaData", {})
        body = msg.get("Message", {}).get(mtype, {})
        mmsi = meta.get("MMSI") or body.get("UserID")

        if mtype in POSITION_TYPES:
            lat = body.get("Latitude", meta.get("latitude", meta.get("Latitude")))
            lon = body.get("Longitude", meta.get("longitude", meta.get("Longitude")))
            sog, nav, hdg = body.get("Sog"), body.get("NavigationalStatus"), body.get("TrueHeading")
            quality["positions"] += 1
            if lat is None or lon is None or abs(lat) > 90 or abs(lon) > 180:
                quality["bad_position"] += 1
                continue
            if sog is not None and sog >= 102.2:
                quality["sog_unavailable"] += 1
            if hdg == 511:
                quality["heading_unavailable"] += 1
            if nav == 15:
                quality["nav_undefined"] += 1
            if not body.get("Valid", True):
                quality["flagged_invalid"] += 1
            reports_per_vessel[mmsi] += 1
            track[mmsi].append([round(lat, 4), round(lon, 4)])
            latest[mmsi] = {"mmsi": mmsi, "name": (meta.get("ShipName") or "").strip(), "lat": lat, "lon": lon,
                            "sog": sog, "cog": body.get("Cog"), "nav_status": nav, "class": "A" if mtype == "PositionReport" else "B",
                            "time": meta.get("time_utc")}
        elif mtype == "ShipStaticData":
            dim = body.get("Dimension") or {}
            eta = body.get("Eta") or {}
            static[mmsi] = {"imo": body.get("ImoNumber"), "type": body.get("Type"), "callsign": (body.get("CallSign") or "").strip(),
                            "destination": (body.get("Destination") or "").strip(),
                            "length_m": (dim.get("A") or 0) + (dim.get("B") or 0), "beam_m": (dim.get("C") or 0) + (dim.get("D") or 0),
                            "draught_m": body.get("MaximumStaticDraught"),
                            "eta": f"{eta.get('Month', 0):02d}-{eta.get('Day', 0):02d} {eta.get('Hour', 0):02d}:{eta.get('Minute', 0):02d}"}

    vessels = []
    for mmsi, v in latest.items():
        s = static.get(mmsi, {})
        sog = v["sog"] if v["sog"] is not None and v["sog"] < 102.2 else None
        if v["nav_status"] == 5:
            state = "moored"
        elif v["nav_status"] == 1 or (sog is not None and sog < 0.5):
            state = "stationary / anchored"
        else:
            state = "under way"
        vessels.append({**v, **s, "sog": sog, "state": state, "category": ship_category(s.get("type")),
                        "region": region(v["lat"], v["lon"]), "reports": reports_per_vessel[mmsi],
                        "nav_text": NAV_STATUS.get(v["nav_status"], str(v["nav_status"]))})

    summary = {
        "file": str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path),
        "first": min(times) if times else None, "last": max(times) if times else None,
        "messages": sum(counts.values()), "by_type": dict(counts.most_common()),
        "per_minute": dict(sorted(per_minute.items())),
        "vessels_with_position": len(latest), "vessels_with_static": len(static),
        "static_coverage": round(len(set(static) & set(latest)) / len(latest), 3) if latest else 0,
        "quality": dict(quality),
        "by_state": dict(Counter(v["state"] for v in vessels)),
        "by_region": dict(Counter(v["region"] for v in vessels).most_common()),
        "by_category": dict(Counter(v["category"] for v in vessels).most_common()),
        "by_region_state": {f"{r}|{s}": n for (r, s), n in Counter((v["region"], v["state"]) for v in vessels).items()},
        "vessels": sorted(vessels, key=lambda v: -v["reports"]),
        "tracks": {str(m): t[:: max(1, len(t) // 40)] for m, t in track.items()},
        "samples": samples,
    }
    out = REPO_ROOT / "data" / "derived" / "sample_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")

    print(f"window {summary['first']} -> {summary['last']}")
    print(f"messages {summary['messages']}  by type {summary['by_type']}")
    print(f"vessels with position {summary['vessels_with_position']}, with static data {summary['vessels_with_static']}"
          f" (static coverage {summary['static_coverage']:.0%})")
    print("quality", summary["quality"])
    print("state", summary["by_state"])
    print("region", summary["by_region"])
    print("category", summary["by_category"])
    print(f"-> {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
