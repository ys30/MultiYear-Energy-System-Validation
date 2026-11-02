"""Deterministic BA-year coverage reporting with file provenance."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .coverage import audit_coverage_csv


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_coverage_report(path, output_dir, *, year, timestamp_column,
                          demand_column, region_column=None, region=None,
                          source_uri=None, retrieved_at=None):
    """Write audit JSON and a one-row Table 1 CSV, without copying raw records."""
    source = Path(path)
    report = audit_coverage_csv(
        source, year=year, timestamp_column=timestamp_column,
        demand_column=demand_column, region_column=region_column, region=region,
    )
    report.update({
        "source_sha256": sha256_file(source),
        "source_uri": source_uri,
        "retrieved_at": retrieved_at,
        "timestamp_contract": "UTC hourly interval start",
        "demand_contract": "verified observed mean MW per hour (caller responsibility)",
        "data_status": "candidate_not_empirically_verified",
    })
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    key = f"{region or 'all'}_{year}"
    (out / f"{key}_audit.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    columns = [
        "year", "region", "rows", "expected_hours", "unique_hours",
        "valid_hours", "missing_hours", "duplicate_rows", "invalid_values",
        "invalid_timestamps", "outside_year", "valid_observed_mwh",
        "complete", "source_sha256", "source_uri", "retrieved_at", "data_status",
    ]
    with (out / f"{key}_table1.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerow({name: report.get(name) for name in columns})
    return report
