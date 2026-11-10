"""Offline, provenance-preserving EIA endpoint comparison.

Input files are JSON arrays of *already downloaded* EIA rows, each with
period/value (and fueltype for fuel rows). This CLI never edits raw inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .eia_cross_endpoint_audit import reconcile_fuel_and_region


def _read_rows(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    obj = json.loads(raw)
    if not isinstance(obj, list) or not all(isinstance(x, dict) for x in obj):
        raise ValueError(f"{path}: expected JSON array of row objects")
    return obj, hashlib.sha256(raw).hexdigest()


def _safe_source_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Source URL must be HTTPS without userinfo")
    query = parse_qsl(parts.query, keep_blank_values=True)
    sensitive = {"api_key", "apikey", "key", "token", "access_token", "authorization"}
    if any(k.lower() in sensitive for k, _ in query):
        raise ValueError("Source URL contains credentials; supply a credential-free URL")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region-json", type=Path, required=True)
    parser.add_argument("--fuel-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--region-url", required=True, help="Exact source URL (not a guess)")
    parser.add_argument("--fuel-url", required=True, help="Exact source URL (not a guess)")
    parser.add_argument("--retrieved-at", required=True, help="Actual UTC ISO8601 source retrieval time")
    args = parser.parse_args(argv)
    if args.output_json.resolve() in {args.region_json.resolve(), args.fuel_json.resolve()}:
        parser.error("Output cannot overwrite raw inputs")
    try:
        timestamp = datetime.fromisoformat(args.retrieved_at.replace("Z", "+00:00"))
    except ValueError as exc:
        parser.error(f"Invalid retrieval timestamp: {exc}")
    if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
        parser.error("Retrieval timestamp must explicitly be UTC")
    try:
        region_url = _safe_source_url(args.region_url)
        fuel_url = _safe_source_url(args.fuel_url)
    except ValueError as exc:
        parser.error(str(exc))
    region, region_hash = _read_rows(args.region_json)
    fuel, fuel_hash = _read_rows(args.fuel_json)
    report = {
        "audit_type": "eia930_fuel_vs_region_ng",
        "source_retrieved_at_utc": timestamp.isoformat(),
        "region_source": {"url": region_url, "sha256": region_hash},
        "fuel_source": {"url": fuel_url, "sha256": fuel_hash},
        "rows": reconcile_fuel_and_region(region, fuel),
        "source_corrected": False,
        "empirical_dispatch_approved": False,
        "note": "Endpoint diagnostic only; raw source rows retained unchanged.",
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
