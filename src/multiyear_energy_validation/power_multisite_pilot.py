"""Multi-site NASA POWER pilot; sites are illustrative, not capacity-weighted."""
import csv
import hashlib
import json
from pathlib import Path

from .power_weather_pilot import fetch_power_hourly

SITES = (
    ("central_valley", 36.5, -119.5),
    ("southern_california", 34.0, -117.5),
    ("northern_california", 39.0, -122.0),
)


def export_multisite(directory, start="20250730", end="20250801"):
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for name, lat, lon in SITES:
        rows = fetch_power_hourly(lat, lon, start, end)
        if len(rows) != 72:
            raise ValueError(f"{name}: expected 72 hours, got {len(rows)}")
        if any(r["ghi_wm2"] == "" or r["wind_speed_10m_ms"] == "" for r in rows):
            raise ValueError(f"{name}: missing resource values")
        path = output / f"power_{name}.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        results.append({
            "site": name, "latitude": lat, "longitude": lon,
            "hours": len(rows), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mean_ghi_wm2": round(sum(float(r["ghi_wm2"]) for r in rows)/len(rows), 3),
            "mean_wind_10m_ms": round(sum(float(r["wind_speed_10m_ms"]) for r in rows)/len(rows), 3),
        })
    manifest = {
        "source": "NASA POWER hourly point API", "start": start, "end": end,
        "sites": results, "site_selection": "illustrative geographic points",
        "capacity_weighted": False, "renewable_availability_approved": False,
        "dispatch_approved": False,
    }
    (output / "multisite.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("NASA_POWER_MULTISITE=" + json.dumps(manifest, sort_keys=True))
    return manifest


if __name__ == "__main__":
    export_multisite("artifacts/r02_weather_multisite")
