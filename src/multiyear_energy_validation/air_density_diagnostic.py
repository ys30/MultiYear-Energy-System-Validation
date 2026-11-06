"""Physics-based meteorological diagnostic: dry-air density from T2M and PS.

This is not wind-turbine power, hub-height wind, or available generation.
"""
import csv
import json
from pathlib import Path
from statistics import mean

R_DRY_AIR = 287.05  # J kg^-1 K^-1
ABSOLUTE_ZERO_C = -273.15


def dry_air_density(pressure_pa, temperature_c):
    p = float(pressure_pa)
    t = float(temperature_c) + 273.15
    if not (50000 <= p <= 110000):
        raise ValueError(f"implausible surface pressure: {p}")
    if not (220 <= t <= 340):
        raise ValueError(f"implausible near-surface air temperature: {t}")
    return p / (R_DRY_AIR * t)


def audit_density(directory):
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    results = []
    for site in manifest["sites"]:
        stem = f"{site['technology']}_plant_{site['plant_id']}"
        with (root/f"{stem}_physical_weather_july2025.csv").open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 744:
            raise ValueError(f"expected 744 hours at {stem}")
        density = [dry_air_density(r["surface_pressure_pa"], r["air_temperature_c"]) for r in rows]
        results.append({
            "plant_id": site["plant_id"], "technology": site["technology"],
            "hours": len(rows),
            "mean_dry_air_density_kg_m3": round(mean(density), 6),
            "min_dry_air_density_kg_m3": round(min(density), 6),
            "max_dry_air_density_kg_m3": round(max(density), 6),
        })
    result = {
        "period": "2025-07",
        "model": "dry-air ideal gas rho=PS/(287.05*(T2M+273.15))",
        "humidity_correction_applied": False,
        "density_is_turbine_output": False,
        "hub_height_wind_validated": False,
        "plant_power_curve_validated": False,
        "dispatch_approved": False,
        "sites": results,
    }
    (root/"dry_air_density_diagnostic.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("DRY_AIR_DENSITY_DIAGNOSTIC="+json.dumps(result,sort_keys=True))
    return result


if __name__ == "__main__":
    audit_density("outputs/spatial_weather_merged_2025")
