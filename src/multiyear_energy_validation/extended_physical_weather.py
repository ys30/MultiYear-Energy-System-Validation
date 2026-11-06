"""Acquire additional NASA POWER weather inputs needed for physical-model research.

These are meteorological inputs, not validated renewable AC potential.
"""
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .power_month_pilot import expected_hours

BASE = "https://power.larc.nasa.gov/api/temporal/hourly/point"
VARIABLES = {
    "ALLSKY_SFC_SW_DWN": "ghi_wm2",
    "ALLSKY_SFC_SW_DNI": "dni_wm2",
    "ALLSKY_SFC_SW_DIFF": "dhi_wm2",
    "T2M": "air_temperature_c",
    "PS": "surface_pressure_kpa",
}
# NASA POWER PS is reported in kPa; convert to Pa for physical-model contracts.
MISSING_CUTOFF = -900


def fetch_extended_weather(latitude, longitude, start="20250701", end="20250731"):
    query = urlencode({
        "parameters": ",".join(VARIABLES),
        "community": "RE", "longitude": str(longitude), "latitude": str(latitude),
        "start": start, "end": end, "format": "JSON", "time-standard": "UTC",
    })
    with urlopen(Request(BASE+"?"+query, headers={"User-Agent": "multiyear-energy-validation/0.1"}),
                 timeout=120) as response:
        payload = json.load(response)
    parameters = payload["properties"]["parameter"]
    expected = expected_hours(start, end)
    rows = []
    for timestamp in expected:
        key = timestamp[:4]+timestamp[5:7]+timestamp[8:10]+timestamp[11:13]
        row = {"period_utc": timestamp}
        for source, target in VARIABLES.items():
            value = float(parameters[source].get(key, -999))
            if value <= MISSING_CUTOFF:
                raise ValueError(f"missing {source} at {timestamp}")
            if source == "PS":
                value *= 1000
                target = "surface_pressure_pa"
            row[target] = value
        if min(row["ghi_wm2"], row["dni_wm2"], row["dhi_wm2"]) < 0:
            raise ValueError("negative irradiance")
        if row["surface_pressure_pa"] <= 0:
            raise ValueError("nonpositive pressure")
        rows.append(row)
    return rows


def export_six_site_extended_weather(pilot_dir, output_dir):
    source = Path(pilot_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((source/"manifest.json").read_text(encoding="utf-8"))
    results = []
    for site in manifest["sites"]:
        rows = fetch_extended_weather(site["latitude"], site["longitude"])
        path = destination/f"{site['technology']}_plant_{site['plant_id']}_extended_july2025.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        results.append({
            "plant_id": site["plant_id"], "technology": site["technology"],
            "hours": len(rows), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "variables": list(rows[0]),
        })
    report = {
        "period": "2025-07", "source": "NASA POWER hourly point API",
        "variables_requested": list(VARIABLES),
        "pressure_conversion": "NASA POWER PS kPa multiplied by 1000 to Pa",
        "sites": results, "total_site_hours": sum(r["hours"] for r in results),
        "plant_metadata_validated": False,
        "weather_to_power_model_validated": False,
        "dispatch_approved": False,
    }
    (destination/"manifest.json").write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("EXTENDED_WEATHER_INPUTS="+json.dumps(report, sort_keys=True))
    return report


if __name__ == "__main__":
    export_six_site_extended_weather("outputs/spatial_weather_pilot_2025",
                                     "outputs/spatial_weather_extended_2025")
