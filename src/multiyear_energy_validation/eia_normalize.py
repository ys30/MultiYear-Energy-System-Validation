"""Strict candidate EIA API row normalization; explicit time semantics required."""
import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def normalize_candidate_rows(rows, output_csv, *, respondent, period_is_utc_interval_end,
                             demand_type="D", units="megawatthours",
                             period_frequency=None):
    """Convert vetted EIA hourly interval-energy observations into UTC mean MW.

    Requires independently confirmed EIA period convention and energy units.
    No raw EIA API fields are assumed to be UTC interval starts.
    """
    if period_frequency != "hourly":
        raise ValueError("EIA API frequency=hourly (UTC) must be explicitly verified")
    if period_is_utc_interval_end is not True:
        raise ValueError("UTC interval-end semantics must be explicitly verified")
    if units != "megawatthours":
        raise ValueError("only hourly MWh interval-energy units supported")
    normalized = []
    for row in rows:
        if row.get("respondent") != respondent or row.get("type") != demand_type:
            raise ValueError("unexpected respondent or series type")
        actual_units = row.get("value-units", row.get("units"))
        if actual_units != units:
            raise ValueError("unexpected EIA units")
        period = row.get("period")
        try:
            stamp = datetime.fromisoformat(period.replace("Z", "+00:00"))
            if stamp.tzinfo is None and period_frequency == "hourly":
                stamp = stamp.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError("invalid period timestamp") from exc
        if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
            raise ValueError("period must include UTC timezone")
        if stamp.minute or stamp.second or stamp.microsecond:
            raise ValueError("period must align to hour")
        try:
            mwh = float(row["value"])
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError("invalid energy value") from exc
        if not math.isfinite(mwh) or mwh < 0:
            raise ValueError("nonfinite or negative energy value")
        normalized.append(((stamp - timedelta(hours=1)).isoformat(), respondent, mwh))
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time_utc", "balancing_authority", "demand_mw"])
        writer.writerows(normalized)
    return len(normalized)
