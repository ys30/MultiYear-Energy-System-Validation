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
    total = math.fsum(values.values())
    return {"year": year, "hours": hours, "annual_mwh": total, "peak_mw": max(values.values()), "min_mw": min(values.values())}
