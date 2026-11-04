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
    largest_ramp_index = max(range(len(hourly_ramps)), key=hourly_ramps.__getitem__)
    ramp_start = start + timedelta(hours=largest_ramp_index)
    ramp_end = ramp_start + timedelta(hours=1)
    ramp_window = [
        {"timestamp_utc": (start + timedelta(hours=i)).isoformat(), "demand_mw": ordered[i]}
        for i in range(max(0, largest_ramp_index - 3), min(hours, largest_ramp_index + 5))
    ]
    isolated_flags = []
    for i in range(1, hours - 1):
        left, current, right = ordered[i - 1:i + 2]
        baseline = (left + right) / 2
        deviation = abs(current - baseline)
        if (baseline > 0 and deviation >= 5000
                and deviation / baseline >= 0.25
                and abs(right - left) <= max(1000, 0.05 * baseline)):
            isolated_flags.append({
                "timestamp_utc": (start + timedelta(hours=i)).isoformat(),
                "observed_mw": current,
                "previous_mw": left,
                "next_mw": right,
                "neighbor_mean_mw": baseline,
                "deviation_from_neighbor_mean_mw": current - baseline,
            })
    # Diagnostic counterfactual only; raw hourly observations remain unchanged.
    counterfactual = ordered.copy()
    for flag in isolated_flags:
        i = int((datetime.fromisoformat(flag["timestamp_utc"]) - start).total_seconds() // 3600)
        counterfactual[i] = flag["neighbor_mean_mw"]
    counterfactual_ramps = [
        abs(b - a) for a, b in zip(counterfactual, counterfactual[1:])
    ]
    sensitivity = {
        "method": "replace only flagged isolated hours with mean of immediate neighbors; diagnostic only",
        "replaced_hours": len(isolated_flags),
        "annual_mwh_observed": total,
        "annual_mwh_hypothetical": math.fsum(counterfactual),
        "annual_mwh_difference": math.fsum(counterfactual) - total,
        "max_absolute_hourly_ramp_mw_observed": max(hourly_ramps),
        "max_absolute_hourly_ramp_mw_hypothetical": max(counterfactual_ramps),
        "not_an_authoritative_correction": True,
    }
    return {
        "isolated_hour_sensitivity": sensitivity,
        "isolated_single_hour_flags": isolated_flags,
        "isolated_single_hour_flag_count": len(isolated_flags),
        "year": year, "hours": hours, "annual_mwh": total,
        "peak_mw": sorted_values[-1], "min_mw": sorted_values[0],
        "mean_mw": total / hours, "median_mw": percentile(0.5),
        "p01_mw": percentile(0.01), "p99_mw": percentile(0.99),
        "zero_load_hours": sum(v == 0 for v in ordered),
        "peak_timestamp_utc": (start + timedelta(hours=ordered.index(sorted_values[-1]))).isoformat(),
        "min_timestamp_utc": (start + timedelta(hours=ordered.index(sorted_values[0]))).isoformat(),
        "max_absolute_hourly_ramp_mw": max(hourly_ramps),
        "max_ramp_from_utc": ramp_start.isoformat(),
        "max_ramp_to_utc": ramp_end.isoformat(),
        "max_ramp_from_mw": ordered[largest_ramp_index],
        "max_ramp_to_mw": ordered[largest_ramp_index + 1],
        "max_ramp_signed_mw": ordered[largest_ramp_index + 1] - ordered[largest_ramp_index],
        "max_ramp_context": ramp_window,
        "min_daily_energy_mwh": min(daily_energy),
        "max_daily_energy_mwh": max(daily_energy),
        "utc_interval_semantics": "hour-start, 1-hour duration",
        "coverage_complete": True,
    }
