"""Fetch NASA POWER weather for actual EIA-860 CISO renewable plant sites.

Bounded four-site engineering pilot, not a regional generation estimate.
"""
import csv
import json
from pathlib import Path
from .power_weather_pilot import fetch_power_hourly
from .renewable_weather_site_selection import select_weather_sites
from .power_month_pilot import expected_hours


def export_actual_plant_weather(geocoded_csv, output_dir, start="20250730", end="20250801"):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    selection = select_weather_sites(geocoded_csv, output / "selection.json", per_technology=2)
    expected = expected_hours(start, end)
    records = []
    for site in selection["selected_sites"]:
        rows = fetch_power_hourly(site["latitude"], site["longitude"], start, end)
        if [r["period_utc"] for r in rows] != expected:
            raise ValueError(f"missing/duplicate hourly records at plant {site['plant_id']}")
        if any(r["ghi_wm2"] == "" or r["wind_speed_10m_ms"] == "" for r in rows):
            raise ValueError(f"missing weather at plant {site['plant_id']}")
        filename = f"{site['technology']}_plant_{site['plant_id']}.csv"
        with (output / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        records.append({
            "plant_id": site["plant_id"], "technology": site["technology"],
            "nameplate_mw": site["nameplate_mw"], "latitude": site["latitude"],
            "longitude": site["longitude"], "hours": len(rows),
            "mean_ghi_wm2": round(sum(float(r["ghi_wm2"]) for r in rows) / len(rows), 3),
            "mean_wind_10m_ms": round(sum(float(r["wind_speed_10m_ms"]) for r in rows) / len(rows), 3),
            "file": filename,
        })
    manifest = {
        "source_weather": "NASA POWER hourly point API",
        "source_plants": "EIA-860 CISO operational solar/wind generators",
        "start": start, "end": end, "plants": records,
        "sample_method": "top two nameplate MW plants per technology",
        "capacity_coverage": selection["coverage"],
        "regional_representativeness_approved": False,
        "wind_hub_height_approved": False,
        "dispatch_approved": False,
    }
    (output / "actual_plant_weather_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("ACTUAL_PLANT_WEATHER=" + json.dumps(manifest, sort_keys=True))
    return manifest


if __name__ == "__main__":
    export_actual_plant_weather("outputs/eia860/2025/ciso_renewable_geocoded_2025.csv",
                                "outputs/actual_plant_weather_2025")
