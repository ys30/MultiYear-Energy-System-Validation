"""Fetch a bounded, reproducible EIA CISO cross-endpoint snapshot.

Writes private CI artifacts only. Never prints or archives API keys.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .eia_cross_endpoint_audit import reconcile_fuel_and_region

ROOT = "https://api.eia.gov/v2/electricity/rto/"
START, END = "2025-07-31T19", "2025-07-31T23"


def _fetch(endpoint: str, key: str, *, kind: str | None = None):
    params = [
        ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[respondent][]", "CISO"),
        ("start", START), ("end", END),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("offset", "0"), ("length", "100"),
    ]
    if kind is not None:
        params.append(("facets[type][]", kind))
    url = ROOT + endpoint + "data/?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "research-audit/1.0"}), timeout=45) as response:
        raw = response.read()
    obj = json.loads(raw)
    payload = obj.get("response", {})
    rows = payload.get("data", [])
    total = int(payload.get("total", -1))
    if not isinstance(rows, list) or total < 0 or total > 100 or len(rows) != total:
        raise ValueError("Incomplete EIA API response")
    if any(row.get("respondent") != "CISO" or not START <= str(row.get("period")) <= END
           for row in rows):
        raise ValueError("EIA facet or period mismatch")
    if kind is not None and any(row.get("type") != kind for row in rows):
        raise ValueError("EIA component mismatch")
    # URL intentionally excludes the secret API key.
    safe_params = [(k, v) for k, v in params if k != "api_key"]
    safe_url = ROOT + endpoint + "data/?" + urlencode(safe_params)
    return rows, raw, safe_url


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    key = os.environ.get("EIA_API_KEY")
    if not key:
        parser.error("EIA_API_KEY secret is required")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    region, region_raw, region_url = _fetch("region-data/", key, kind="NG")
    fuel, fuel_raw, fuel_url = _fetch("fuel-type-data/", key)
    for rows, name in ((region, "region"), (fuel, "fuel")):
        if any(str(r.get("value-units", "")).lower() != "megawatthours" for r in rows):
            raise ValueError(f"Unexpected {name} energy units")
    # Do not publish raw responses in logs; archive privately with retention controls.
    (out / "region_raw.json").write_bytes(region_raw)
    (out / "fuel_raw.json").write_bytes(fuel_raw)
    result = reconcile_fuel_and_region(region, fuel, fuel_key="fueltype")
    expected = [f"2025-07-31T{hour:02d}" for hour in range(19, 24)]
    if [row["period"] for row in result] != expected:
        raise ValueError("Five-hour period coverage incomplete")
    report = {
        "retrieved_at_utc": retrieved_at,
        "source": {
            "region": {"url_without_credentials": region_url, "sha256": hashlib.sha256(region_raw).hexdigest()},
            "fuel": {"url_without_credentials": fuel_url, "sha256": hashlib.sha256(fuel_raw).hexdigest()},
        },
        "rows": result,
        "source_corrected": False,
        "empirical_dispatch_approved": False,
        "interpretation": "Unverified cross-endpoint diagnostic; no correction or availability inference",
    }
    (out / "cross_endpoint_audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("R02A_CROSS_ENDPOINT_SUMMARY=" + json.dumps({
        "periods": len(result),
        "fuel_minus_region_mwh": [r["fuel_minus_region_mwh"] for r in result],
        "empirical_dispatch_approved": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
