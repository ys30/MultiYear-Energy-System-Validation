"""Normalize observed EIA hourly fuel records without imputing unavailable generation.

Output is an observational table, not renewable potential or dispatch input.
"""
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

FUELS = ("COL", "GEO", "NG", "NUC", "OIL", "OTH", "SUN", "WAT", "WND")


def expected_utc_hours(year):
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    hours = []
    while start < end:
        hours.append(start.strftime("%Y-%m-%dT%H"))
        start += timedelta(hours=1)
    return hours


def normalize_fuel_records(records, year):
    """One row per expected UTC hour and fuel; missing values stay None."""
    periods = expected_utc_hours(year)
    expected = set(periods)
    observed = {}
    for record in records:
        if record["respondent"] != "CISO":
            raise ValueError("unexpected balancing authority")
        if record["value-units"] != "megawatthours":
            raise ValueError("unexpected energy unit")
        period, fuel = record["period"], record["fueltype"]
        if period not in expected or fuel not in FUELS:
            raise ValueError("unexpected period or fuel")
        key = (period, fuel)
        if key in observed:
            raise ValueError("duplicate period/fuel record")
        observed[key] = float(record["value"])
    first_geo = min((period for period, fuel in observed if fuel == "GEO"), default=None)
    rows = []
    for period in periods:
        for fuel in FUELS:
            value = observed.get((period, fuel))
            rows.append({
                "period_utc_eia": period,
                "respondent": "CISO",
                "fueltype": fuel,
                "observed_generation_mwh": value,
                "observation_status": "observed" if value is not None else "not_reported",
                "taxonomy_boundary_flag": bool(first_geo and fuel == "GEO" and period < first_geo),
                "availability_estimate": False,
            })
    return rows


def write_normalized(rows, destination, metadata):
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "period_utc_eia", "respondent", "fueltype", "observed_generation_mwh",
            "observation_status", "taxonomy_boundary_flag", "availability_estimate"])
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {**metadata, "sha256": digest, "row_count": len(rows),
                "observed_record_count": sum(row["observation_status"] == "observed" for row in rows),
                "not_reported_count": sum(row["observation_status"] == "not_reported" for row in rows),
                "missing_values_imputed": False,
                "observed_generation_is_renewable_availability": False}
    path.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest
