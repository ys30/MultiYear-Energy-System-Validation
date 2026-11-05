"""Bounded public NASA POWER hourly weather acquisition pilot.

Pilot is weather-data engineering only, NOT a CISO renewable-potential estimate.
"""
import csv
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://power.larc.nasa.gov/api/temporal/hourly/point"


def fetch_power_hourly(lat, lon, start, end):
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,WS10M",
        "community": "RE",
        "longitude": str(lon), "latitude": str(lat),
        "start": start, "end": end, "format": "JSON",
        "time-standard": "UTC",
    }
    url = BASE + "?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "multiyear-energy-validation/0.1"}),
                 timeout=120) as response:
        payload = json.load(response)
    data = payload["properties"]["parameter"]
    radiation = data["ALLSKY_SFC_SW_DWN"]
    wind = data["WS10M"]
    keys = sorted(set(radiation) | set(wind))
    rows = []
    for key in keys:
        dt = datetime.strptime(key, "%Y%m%d%H").replace(tzinfo=timezone.utc)
        ghi = float(radiation.get(key, -999))
        ws = float(wind.get(key, -999))
        rows.append({
            "period_utc": dt.strftime("%Y-%m-%dT%H"),
            "ghi_wm2": "" if ghi <= -900 else ghi,
            "wind_speed_10m_ms": "" if ws <= -900 else ws,
            "source": "NASA POWER hourly point",
            "latitude": lat, "longitude": lon,
        })
    return rows


def export_pilot(destination, lat=36.5, lon=-119.5, start="20250730", end="20250801"):
    rows = fetch_power_hourly(lat, lon, start, end)
    expected_start = datetime.strptime(start, "%Y%m%d")
    expected_end = datetime.strptime(end, "%Y%m%d") + timedelta(days=1)
    expected = []
    while expected_start < expected_end:
        expected.append(expected_start.strftime("%Y-%m-%dT%H"))
        expected_start += timedelta(hours=1)
    periods = [row["period_utc"] for row in rows]
    if periods != expected:
        raise ValueError(f"hour coverage mismatch: expected {len(expected)}, observed {len(periods)}")
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "source": "NASA POWER hourly point API",
        "variables": ["ALLSKY_SFC_SW_DWN", "WS10M"],
        "units": {"ghi_wm2": "W/m2", "wind_speed_10m_ms": "m/s"},
        "time_standard": "UTC",
        "start_date": start, "end_date": end,
        "latitude": lat, "longitude": lon,
        "hour_count": len(rows),
        "missing_ghi_hours": sum(row["ghi_wm2"] == "" for row in rows),
        "missing_wind_hours": sum(row["wind_speed_10m_ms"] == "" for row in rows),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "representative_ciso_capacity_weighted": False,
        "wind_hub_height_validated": False,
        "renewable_availability_approved": False,
        "r02_dispatch_approved": False,
    }
    path.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("NASA_POWER_PILOT=" + json.dumps(manifest, sort_keys=True))
    return manifest


if __name__ == "__main__":
    export_pilot(os.environ.get("POWER_PILOT_OUTPUT", "artifacts/r02_weather/power_hourly_pilot.csv"))
