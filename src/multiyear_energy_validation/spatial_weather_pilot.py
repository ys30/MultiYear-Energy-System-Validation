"""Acquire July weather for a bounded six-site geographically stratified pilot.

The selected sites are a spatial design sample, not a validated representation
of CAISO generation or renewable availability.
"""
import csv
import hashlib
import json
from pathlib import Path

from .power_month_pilot import expected_hours
from .power_weather_pilot import fetch_power_hourly
from .renewable_spatial_sample import spatial_sample_design


def export_spatial_weather_pilot(geocoded_csv, output_dir, start="20250701", end="20250731"):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    selection = spatial_sample_design(geocoded_csv, output/"spatial_selection.json",
                                      per_technology=3, grid_degrees=1.0)
    expected = expected_hours(start, end)
    results = []
    for site in selection["sites"]:
        rows = fetch_power_hourly(site["latitude"], site["longitude"], start, end)
        if [r["period_utc"] for r in rows] != expected:
            raise ValueError(f"incomplete time axis: {site['plant_id']}")
        if any(r["ghi_wm2"] == "" or r["wind_speed_10m_ms"] == "" for r in rows):
            raise ValueError(f"missing weather values: {site['plant_id']}")
        filename = f"{site['technology']}_plant_{site['plant_id']}_july2025.csv"
        path = output/filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        results.append({**site, "hours": len(rows),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {
        "period": "2025-07", "source": "NASA POWER hourly point API",
        "selection": selection["technology"], "sites": results,
        "total_site_hours": sum(site["hours"] for site in results),
        "weather_representativeness_approved": False,
        "renewable_availability_approved": False,
        "dispatch_approved": False,
    }
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("SPATIAL_WEATHER_PILOT="+json.dumps(manifest, sort_keys=True))
    return manifest


if __name__ == "__main__":
    export_spatial_weather_pilot("outputs/eia860/2025/ciso_renewable_geocoded_2025.csv",
                                 "outputs/spatial_weather_pilot_2025")
