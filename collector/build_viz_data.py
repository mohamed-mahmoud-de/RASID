"""Build a compact JSON payload for the coverage illustration.

Combines the Egypt-box capture, the wide coverage probe, and PortWatch reference data.
Usage: python collector/build_viz_data.py <egypt_ndjson> <probe_ndjson>
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POSITION_TYPES = {"PositionReport", "StandardClassBPositionReport", "ExtendedClassBPositionReport"}


def load(path: Path) -> list[dict]:
    return [json.loads(line)["msg"] for line in path.read_text(encoding="utf-8").splitlines()]


def latest_positions(msgs: list[dict]) -> dict[int, list]:
    latest: dict[int, list] = {}
    for m in msgs:
        t = m.get("MessageType")
        if t not in POSITION_TYPES:
            continue
        body = m["Message"][t]
        lat, lon = body.get("Latitude"), body.get("Longitude")
        if lat is None or lon is None or abs(lat) > 90 or abs(lon) > 180:
            continue
        latest[m["MetaData"]["MMSI"]] = [round(lat, 3), round(lon, 3), "A" if t == "PositionReport" else "B"]
    return latest


def main(egypt_path: Path, probe_path: Path) -> None:
    egypt, probe = load(egypt_path), load(probe_path)
    eg_pos, pr_pos = latest_positions(egypt), latest_positions(probe)
    suez = json.loads((REPO_ROOT / "data/reference/portwatch_suez_daily.json").read_text())
    payload = {
        "egypt": {"messages": len(egypt), "by_type": dict(Counter(m["MessageType"] for m in egypt)),
                  "vessels": len(eg_pos), "points": list(eg_pos.values())},
        "probe": {"messages": len(probe), "by_type": dict(Counter(m["MessageType"] for m in probe)),
                  "vessels": len(pr_pos), "points": list(pr_pos.values())},
        "suez": {"dates": [r["date"] for r in suez], "n": [r["n_total"] for r in suez]},
    }
    out = REPO_ROOT / "data/derived/viz_payload.json"
    out.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"egypt {payload['egypt']['messages']} msgs / {payload['egypt']['vessels']} vessels; "
          f"probe {payload['probe']['messages']} msgs / {payload['probe']['vessels']} vessels; -> {out} "
          f"({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
