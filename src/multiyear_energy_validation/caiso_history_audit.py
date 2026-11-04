"""Independent CAISO Today's Outlook historical demand CSV diagnostic.

This does not assume the CAISO telemetry and EIA-930 demand definitions match.
"""
import csv
import io
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

URL = "https://www.caiso.com/outlook/history/20250731/demand.csv"


def inspect_csv(payload):
    reader = csv.DictReader(io.StringIO(payload))
    headers = reader.fieldnames or []
    rows = list(reader)
    if not rows:
        raise ValueError("empty CAISO historical demand CSV")
    # July 31 is PDT (UTC-7); 20:00 UTC corresponds to 13:00 local.
    # Exclude the final repeated 00:00 row (next day's boundary).
    by_time = {}
    for row in rows:
        time = row.get("Time", "")
        if time in by_time:
            continue
        try:
            value = float(row["Current demand"])
        except (KeyError, TypeError, ValueError):
            continue
        by_time[time] = value
    def hour_values(hour):
        return [by_time[f"{hour:02d}:{minute:02d}"]
                for minute in range(0, 60, 5)
                if f"{hour:02d}:{minute:02d}" in by_time]
    windows = {}
    for hour in (12, 13, 14):
        values = hour_values(hour)
        windows[f"{hour:02d}:00"] = {
            "five_minute_samples": len(values),
            "mean_mw": sum(values) / len(values) if values else None,
            "min_mw": min(values) if values else None,
            "max_mw": max(values) if values else None,
            "values_mw": values,
        }
    # Compare temporal shape only: sources may have different load scope.
    # EIA values are archived, verified hourly observations, not CAISO corrections.
    eia_hours = {"12:00": 29881.0, "13:00": 11819.0, "14:00": 29886.0}
    comparison = {}
    for a, b in (("12:00", "13:00"), ("13:00", "14:00")):
        ca = windows[a]["mean_mw"]
        cb = windows[b]["mean_mw"]
        comparison[f"{a}_to_{b}"] = {
            "eia_change_mw": eia_hours[b] - eia_hours[a],
            "caiso_change_mw": cb - ca if ca is not None and cb is not None else None,
            "same_change_direction": (
                (eia_hours[b] - eia_hours[a]) * (cb - ca) > 0
                if ca is not None and cb is not None else None
            ),
        }
    comparison["all_hours_complete"] = all(
        windows[hour]["five_minute_samples"] == 12 for hour in eia_hours
    )
    return {
        "hourly_shape_comparison": comparison,
        "local_hour_windows": windows,
        "source_url": URL,
        "source": "CAISO Today's Outlook historical demand (telemetry)",
        "independent_of_eia930": True,
        "comparison_status": "schema_review_required",
        "columns": headers,
        "row_count": len(rows),
        "sample_first": rows[:2],
        "sample_last": rows[-2:],
        "target_local_window": "2025-07-31 12:00–15:00 America/Los_Angeles",
        "target_utc_hour_start": "2025-07-31T20:00:00+00:00",
        "note": "Do not compare raw MW directly until telemetry scope and time semantics are checked.",
    }


def main():
    request = Request(URL, headers={"User-Agent": "ResearchDataAudit/1.0"})
    with urlopen(request, timeout=40) as response:
        payload = response.read().decode("utf-8-sig")
    print("CAISO_HISTORICAL_DEMAND_AUDIT=" + json.dumps(inspect_csv(payload), sort_keys=True))


if __name__ == "__main__":
    main()
