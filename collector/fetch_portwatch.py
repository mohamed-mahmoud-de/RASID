"""Download IMF PortWatch reference data (free, no API key) into data/reference/.

Usage: python collector/fetch_portwatch.py

- portwatch_suez_daily.json: daily Suez Canal transits by vessel type (last 365 days)
- portwatch_egypt_ports_daily.json: daily port calls for Alexandria, Port Said, Damietta
"""

from __future__ import annotations

import datetime
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/{svc}/FeatureServer/0/query"


def day(value) -> str:
    if isinstance(value, (int, float)):
        return str(datetime.datetime.fromtimestamp(value / 1000, datetime.UTC).date())
    return str(value)[:10].replace("/", "-")


def query(svc: str, where: str, fields: str, limit: int, attempts: int = 4) -> list[dict]:
    """One ArcGIS query (limit must stay <= 1000, the server's page size), retried with backoff."""
    params = urllib.parse.urlencode({"where": where, "outFields": fields, "orderByFields": "date DESC",
                                     "resultRecordCount": limit, "f": "json"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(BASE.format(svc=svc) + "?" + params, timeout=90) as resp:
                data = json.load(resp)
            if "features" in data:
                rows = [{**f["attributes"], "date": day(f["attributes"]["date"])} for f in data["features"]]
                return sorted(rows, key=lambda r: r["date"])
            error = str(data)[:300]
        except OSError as exc:
            error = repr(exc)
        print(f"{svc} attempt {attempt}/{attempts} failed: {error}")
        time.sleep(5 * attempt)
    raise RuntimeError(f"{svc}: giving up after {attempts} attempts")


def main() -> None:
    out_dir = REPO_ROOT / "data" / "reference"
    out_dir.mkdir(parents=True, exist_ok=True)
    suez = query("Daily_Chokepoints_Data", "portname='Suez Canal'",
                 "date,n_total,n_container,n_tanker,n_dry_bulk,n_general_cargo,n_roro", 365)
    (out_dir / "portwatch_suez_daily.json").write_text(json.dumps(suez, indent=0))
    ports = []
    for port in ("Alexandria", "Port Said", "Damietta"):
        ports += query("Daily_Ports_Data", f"portname='{port}' AND country='Egypt'",
                       "date,portname,country,portcalls,portcalls_container,portcalls_tanker,portcalls_dry_bulk", 365)
    ports.sort(key=lambda r: (r["date"], r["portname"]))
    (out_dir / "portwatch_egypt_ports_daily.json").write_text(json.dumps(ports, indent=0))
    print(f"suez: {len(suez)} days ({suez[0]['date']} -> {suez[-1]['date']}); ports: {len(ports)} rows -> {out_dir}")


if __name__ == "__main__":
    main()
