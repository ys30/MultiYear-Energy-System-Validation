"""Fetch, validate and export CISO EIA fuel observations as reproducible artifacts."""
import json
import os
from pathlib import Path

from .eia_fuel_year_audit import audit_year, fetch_year
from .normalized_fuel import normalize_fuel_records, write_normalized


def export_year(key, year, directory):
    records = fetch_year(key, year)
    audit = audit_year(records, year)
    if audit["invalid_row_count"] or audit["unexpected_periods"]:
        raise ValueError("invalid EIA rows or unexpected periods")
    rows = normalize_fuel_records(records, year)
    destination = Path(directory) / f"ciso_eia_fuel_{year}_normalized.csv"
    manifest = write_normalized(rows, destination, {
        "source": "EIA API v2 electricity/rto/fuel-type-data",
        "respondent": "CISO",
        "year": year,
        "source_record_count": len(records),
        "source_observed_hour_count": audit["observed_hours"],
        "source_expected_hour_count": audit["expected_hours"],
        "source_missing_utc_hours": audit["missing_periods"],
        "source_coverage_pass": audit["coverage_pass"],
        "source_fuel_first_last_and_hours": audit["fuel_first_last_and_hours"],
        "time_label_semantics": "native EIA UTC hourly period; no hour shift",
        "units": "megawatthours",
    })
    if manifest["observed_record_count"] != len(records):
        raise ValueError("export observed row count mismatch")
    print("EIA_NORMALIZED_EXPORT=" + json.dumps({
        "year": year, "file": str(destination), "sha256": manifest["sha256"],
        "observed_records": manifest["observed_record_count"],
        "not_reported_cells": manifest["not_reported_count"],
        "missing_utc_hours": len(audit["missing_periods"]),
        "coverage_pass": audit["coverage_pass"],
        "model_input_approved": False,
    }, sort_keys=True))
    return manifest


def main():
    key = os.environ["EIA_API_KEY"]
    directory = os.environ.get("R02_EXPORT_DIR", "artifacts/r02_eia_fuel")
    for year in (2024, 2025):
        export_year(key, year, directory)


if __name__ == "__main__":
    main()
