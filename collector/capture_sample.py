"""Capture a raw AIS sample from aisstream.io into Bronze (NDJSON).

Usage:
    python collector/capture_sample.py --minutes 10

Reads AISSTREAM_API_KEY from the environment or from the repo-root .env file.
Each output line is {"received_at": <UTC ISO-8601>, "msg": <message exactly as received>}.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

URL = "wss://stream.aisstream.io/v0/stream"
REPO_ROOT = Path(__file__).resolve().parents[1]

# One box covering Alexandria -> Damietta -> Port Said -> canal -> Suez, plus Med approaches.
# Corners are [lat, lon]. Collect wide, model narrow (decision P-010).
EGYPT_BBOX = [[[29.5, 29.5], [33.5, 34.5]]]


def load_api_key() -> str:
    key = os.environ.get("AISSTREAM_API_KEY", "").strip()
    env_file = REPO_ROOT / ".env"
    if not key and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "AISSTREAM_API_KEY":
                key = value.strip().strip('"').strip("'")
    if not key:
        sys.exit("AISSTREAM_API_KEY is not set. Put it in .env at the repo root (see .env.example).")
    return key


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


async def capture(minutes: float, out_dir: Path, types: list[str] | None, bbox: list | None = None) -> Path:
    key = load_api_key()
    subscription = {"APIKey": key, "BoundingBoxes": bbox or EGYPT_BBOX}
    if types:
        subscription["FilterMessageTypes"] = types

    started = datetime.now(timezone.utc)
    out_path = out_dir / f"date={started:%Y-%m-%d}" / f"ais_{started:%Y%m%dT%H%M%SZ}.ndjson"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    deadline = time.monotonic() + minutes * 60
    counts: Counter[str] = Counter()
    mmsis: set[int] = set()
    backoff = 1.0
    last_report = time.monotonic()

    with out_path.open("w", encoding="utf-8") as out:
        while time.monotonic() < deadline:
            try:
                async with connect(URL, open_timeout=10, ping_interval=20) as ws:
                    await ws.send(json.dumps(subscription))  # must arrive within 3 s
                    print(f"[{utc_now()}] connected, subscribed", flush=True)
                    while (remaining := deadline - time.monotonic()) > 0:
                        try:
                            frame = await asyncio.wait_for(ws.recv(), timeout=min(remaining, 30))
                        except asyncio.TimeoutError:
                            if deadline - time.monotonic() > 0:
                                print(f"[{utc_now()}] no messages in 30 s", flush=True)
                            continue
                        msg = json.loads(frame)
                        if msg.get("MessageType") == "SubscriptionConfirmation":
                            continue
                        if "error" in msg:
                            print(f"[{utc_now()}] server error: {msg['error']}", flush=True)
                            continue
                        out.write(json.dumps({"received_at": utc_now(), "msg": msg}) + "\n")
                        counts[msg.get("MessageType", "?")] += 1
                        if mmsi := msg.get("MetaData", {}).get("MMSI"):
                            mmsis.add(mmsi)
                        backoff = 1.0
                        if time.monotonic() - last_report >= 30:
                            last_report = time.monotonic()
                            out.flush()
                            print(f"[{utc_now()}] {sum(counts.values())} msgs, "
                                  f"{len(mmsis)} vessels, {dict(counts.most_common(4))}", flush=True)
                    break
            except (ConnectionClosed, OSError, TimeoutError) as exc:
                print(f"[{utc_now()}] disconnected: {exc!r}; retrying in {backoff:.0f} s", flush=True)
                if not counts:
                    print("  (no messages yet - check the API key and connection limits)", flush=True)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    print(f"[{utc_now()}] done: {sum(counts.values())} msgs, {len(mmsis)} vessels -> {out_path}")
    print("message types:", dict(counts.most_common()))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--minutes", type=float, default=10)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "data" / "bronze" / "sample")
    parser.add_argument("--types", nargs="*", help="optional FilterMessageTypes, e.g. PositionReport ShipStaticData")
    parser.add_argument("--bbox", nargs=4, type=float, metavar=("LAT1", "LON1", "LAT2", "LON2"),
                        help="override the default Egypt box")
    args = parser.parse_args()
    bbox = [[args.bbox[:2], args.bbox[2:]]] if args.bbox else None
    asyncio.run(capture(args.minutes, args.out, args.types, bbox))


if __name__ == "__main__":
    main()
