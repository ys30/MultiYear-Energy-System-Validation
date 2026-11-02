"""EIA-930-style CSV intake with explicit field mappings and UTC timestamps.

This is a format adapter, not an automatic EIA download. The caller must verify
that selected source fields represent observed demand MW, not forecast or net
generation, and that timestamps are UTC hourly interval starts.
"""
import csv
from datetime import datetime, timezone
from pathlib import Path
from .timeseries import validate_utc_hourly

def audit_csv(path, *, year, timestamp_column, demand_column, region_column=None, region=None):
    if region is not None and region_column is None:
        raise ValueError("region_column required when filtering by region")
    records = []
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        needed = {timestamp_column, demand_column}
        if region_column:
            needed.add(region_column)
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError("required columns missing")
        for row in reader:
            if region is not None and row[region_column] != region:
                continue
            stamp = datetime.fromisoformat(row[timestamp_column].replace("Z", "+00:00"))
            if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
                raise ValueError("timestamps must include explicit UTC offset")
            if row[demand_column] is None or row[demand_column].strip() == "":
                raise ValueError("missing demand MW")
            records.append((stamp, float(row[demand_column])))
    return validate_utc_hourly(records, year)
