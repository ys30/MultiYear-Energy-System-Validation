"""UTC hourly load validation with explicit year and interval contracts."""
import calendar
import math
from datetime import datetime, timedelta, timezone

def validate_utc_hourly(records, year: int):
    """Validate complete hourly UTC (timestamp, MW) observations for a calendar year.

    Return a dictionary of audited totals. Reject duplicates, gaps, out-of-year
    observations, non-UTC timestamps, negative loads and non-finite values.
    Timestamps represent the start of a one-hour interval.
    """
    if not isinstance(year, int) or isinstance(year, bool) or year < 1900:
        raise ValueError("invalid year")
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    hours = (366 if calendar.isleap(year) else 365) * 24
    end = start + timedelta(hours=hours)
    values = {}
    for stamp, mw in records:
        if not isinstance(stamp, datetime) or stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
            raise ValueError("timestamps must be timezone-aware UTC")
        if stamp.minute or stamp.second or stamp.microsecond:
            raise ValueError("timestamps must start on the hour")
        if not start <= stamp < end:
            raise ValueError("timestamp outside requested UTC calendar year")
        if stamp in values:
            raise ValueError("duplicate UTC timestamp")
        if not isinstance(mw, (int, float)) or not math.isfinite(mw) or mw < 0:
            raise ValueError("load MW must be finite and nonnegative")
        values[stamp] = float(mw)
    if len(values) != hours:
        raise ValueError(f"incomplete hourly coverage: {len(values)}/{hours}")
    for i in range(hours):
        if start + timedelta(hours=i) not in values:
            raise ValueError("missing hourly timestamp")
    ordered = [values[start + timedelta(hours=i)] for i in range(hours)]
    total = math.fsum(ordered)
    sorted_values = sorted(ordered)
    def percentile(p):
        pos = (hours - 1) * p
        low = int(pos)
        fraction = pos - low
        return sorted_values[low] * (1 - fraction) + sorted_values[min(low + 1, hours - 1)] * fraction
    daily_energy = [math.fsum(ordered[i:i + 24]) for i in range(0, hours, 24)]
    hourly_ramps = [abs(b - a) for a, b in zip(ordered, ordered[1:])]
    return {
        "year": year, "hours": hours, "annual_mwh": total,
        "peak_mw": sorted_values[-1], "min_mw": sorted_values[0],
        "mean_mw": total / hours, "median_mw": percentile(0.5),
        "p01_mw": percentile(0.01), "p99_mw": percentile(0.99),
        "zero_load_hours": sum(v == 0 for v in ordered),
        "peak_timestamp_utc": (start + timedelta(hours=ordered.index(sorted_values[-1]))).isoformat(),
        "min_timestamp_utc": (start + timedelta(hours=ordered.index(sorted_values[0]))).isoformat(),
        "max_absolute_hourly_ramp_mw": max(hourly_ramps),
        "min_daily_energy_mwh": min(daily_energy),
        "max_daily_energy_mwh": max(daily_energy),
        "utc_interval_semantics": "hour-start, 1-hour duration",
        "coverage_complete": True,
    }
