"""Non-destructive UTC coverage audit; no imputation or empirical claims."""
import calendar
import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def audit_coverage_csv(path, *, year, timestamp_column, demand_column,
                       region_column=None, region=None):
    """Report incomplete BA-year coverage without silently dropping bad rows.

    Input contract: hourly interval-start timestamps with explicit UTC offset,
    observed demand in MW, and optionally a balancing-authority identifier.
    Source semantics must be independently verified before ingestion.
    """
    if region is not None and not region_column:
        raise ValueError("region_column required when filtering by region")
    if not isinstance(year, int) or isinstance(year, bool) or year < 1900:
        raise ValueError("invalid year")
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    expected = (366 if calendar.isleap(year) else 365) * 24
    end = start + timedelta(hours=expected)
    seen = set()
    duplicates = invalid_values = invalid_timestamps = outside_year = 0
    valid_mwh = 0.0
    rows = 0
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {timestamp_column, demand_column}
        if region_column:
            required.add(region_column)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("required columns missing")
        for row in reader:
            if region is not None and row[region_column] != region:
                continue
            rows += 1
            try:
                stamp = datetime.fromisoformat(row[timestamp_column].replace("Z", "+00:00"))
                if (stamp.tzinfo is None or stamp.utcoffset() != timedelta(0)
                        or stamp.minute or stamp.second or stamp.microsecond):
                    raise ValueError("not UTC hourly")
            except (ValueError, TypeError, AttributeError):
                invalid_timestamps += 1
                continue
            if not start <= stamp < end:
                outside_year += 1
                continue
            if stamp in seen:
                duplicates += 1
                continue
            seen.add(stamp)
            try:
                mw = float(row[demand_column])
                if not math.isfinite(mw) or mw < 0:
                    raise ValueError("invalid MW")
            except (ValueError, TypeError):
                invalid_values += 1
                continue
            valid_mwh += mw  # one-hour mean MW -> MWh
    valid_hours = len(seen) - invalid_values
    return {
        "year": year, "region": region, "rows": rows,
        "expected_hours": expected, "unique_hours": len(seen),
        "valid_hours": valid_hours, "missing_hours": expected - len(seen),
        "duplicate_rows": duplicates, "invalid_values": invalid_values,
        "invalid_timestamps": invalid_timestamps, "outside_year": outside_year,
        "valid_observed_mwh": valid_mwh,
        "complete": (valid_hours == expected and duplicates == 0
                     and invalid_timestamps == 0 and outside_year == 0
                     and invalid_values == 0),
    }
