"""Full-month NASA POWER observations at four verified CISO plant locations.

Data acquisition only; no renewable power conversion or regional inference.
"""
import csv
import hashlib
import json
from pathlib import Path

from .power_month_pilot import expected_hours
from .power_weather_pilot import fetch_power_hourly
from .renewable_weather_site_selection import select_weather_sites


def export_month_at_actual_plants(geocoded_csv, output_dir, start="20250701", end="20250731"):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    selection = select_weather_sites(geocoded_csv, output / "selection.json", per_technology=2)
    expected = expected_hours(start, end)
    results = []
    for site in selection["selected_sites"]:
        rows = fetch_power_hourly(site["latitude"], site["longitude"], start, end)
        if [r["period_utc"] for r in rows] != expected:
            raise ValueError(f"hour coverage mismatch: plant {site['plant_id']}")
        missing_ghi = sum(r["ghi_wm2"] == "" for r in rows)
        missing_wind = sum(r["wind_speed_10m_ms"] == "" for r in rows)
        if missing_ghi or missing_wind:
            raise ValueError(f"missing observations at plant {site['plant_id']}: GHI={missing_ghi} wind={missing_wind}")
        filename = f"{site['technology']}_plant_{site['plant_id']}_july2025.csv"
        path = output / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        results.append({
            **site, "hours": len(rows), "missing_ghi": missing_ghi,
            "missing_wind": missing_wind,
            "mean_ghi_wm2": round(sum(float(r["ghi_wm2"]) for r in rows)/len(rows), 3),
            "mean_wind_10m_ms": round(sum(float(r["wind_speed_10m_ms"]) for r in rows)/len(rows), 3),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    manifest = {
        "source_weather": "NASA POWER hourly point API",
        "source_plants": "EIA-860 2025 CISO OP solar/wind",
        "period_start": start, "period_end": end,
        "capacity_coverage": selection["coverage"], "plants": results,
        "regional_weather_representative": False,
        "renewable_availability_approved": False, "dispatch_approved": False,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("ACTUAL_PLANT_WEATHER_MONTH=" + json.dumps(manifest, sort_keys=True))
    return manifest


if __name__ == "__main__":
    export_month_at_actual_plants(
        "outputs/eia860/2025/ciso_renewable_geocoded_2025.csv",
        "outputs/actual_plant_weather_month_2025",
    )
