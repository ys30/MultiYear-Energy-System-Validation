"""Month-scale, multi-site weather pilot with reproducible hourly coverage checks."""
import csv
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

from .power_multisite_pilot import SITES
from .power_weather_pilot import fetch_power_hourly


def expected_hours(start, end):
    first = datetime.strptime(start, "%Y%m%d")
    stop = datetime.strptime(end, "%Y%m%d") + timedelta(days=1)
    result = []
    while first < stop:
        result.append(first.strftime("%Y-%m-%dT%H"))
        first += timedelta(hours=1)
    return result


def export_month(directory, start="20250701", end="20250731"):
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    expected = expected_hours(start, end)
    sites = []
    for name, lat, lon in SITES:
        rows = fetch_power_hourly(lat, lon, start, end)
        periods = [row["period_utc"] for row in rows]
        if periods != expected:
            raise ValueError(f"{name}: incomplete or duplicate UTC hour sequence")
        missing_ghi = sum(row["ghi_wm2"] == "" for row in rows)
        missing_wind = sum(row["wind_speed_10m_ms"] == "" for row in rows)
        if missing_ghi or missing_wind:
            raise ValueError(f"{name}: missing GHI={missing_ghi}, wind={missing_wind}")
        path = target / f"power_{name}_{start}_{end}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        sites.append({
            "site": name, "latitude": lat, "longitude": lon,
            "hours": len(rows), "missing_ghi": missing_ghi,
            "missing_wind": missing_wind,
            "mean_ghi_wm2": round(sum(float(row["ghi_wm2"]) for row in rows)/len(rows), 3),
            "mean_wind_10m_ms": round(sum(float(row["wind_speed_10m_ms"]) for row in rows)/len(rows), 3),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    result = {
        "source": "NASA POWER hourly point API", "start": start, "end": end,
        "expected_hours_per_site": len(expected), "sites": sites,
        "capacity_weighted": False, "renewable_availability_approved": False,
        "r02_dispatch_approved": False,
    }
    (target / "month.manifest.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("NASA_POWER_MONTH=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    export_month("artifacts/r02_weather_month")
