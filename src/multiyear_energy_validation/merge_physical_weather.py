"""Join independently archived NASA POWER base and extended weather by UTC hour.

Reject any timestamp mismatch or GHI disagreement; do not silently overwrite
observations. This prepares physical model input without estimating power.
"""
import csv
import json
from pathlib import Path

from .physical_conversion_readiness import assess_site


def merge_site_weather(base_dir, extended_dir, output_dir):
    base, ext, out = Path(base_dir), Path(extended_dir), Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((base/"manifest.json").read_text(encoding="utf-8"))
    audit = []
    for site in manifest["sites"]:
        stem = f"{site['technology']}_plant_{site['plant_id']}"
        with (base/f"{stem}_july2025.csv").open(newline="", encoding="utf-8") as handle:
            original = list(csv.DictReader(handle))
        with (ext/f"{stem}_extended_july2025.csv").open(newline="", encoding="utf-8") as handle:
            supplemental = list(csv.DictReader(handle))
        if len(original) != 744 or len(supplemental) != 744:
            raise ValueError(f"incomplete hourly data at {stem}")
        times_original = [r["period_utc"] for r in original]
        times_extended = [r["period_utc"] for r in supplemental]
        if times_original != times_extended or len(set(times_original)) != 744:
            raise ValueError(f"duplicate or misaligned UTC hours at {stem}")
        rows = []
        ghi_diffs = []
        for a,b in zip(original,supplemental):
            ghi_diffs.append(abs(float(a["ghi_wm2"])-float(b["ghi_wm2"])))
            combined = dict(a)
            for key,value in b.items():
                if key not in ("period_utc", "ghi_wm2"):
                    if key in combined:
                        raise ValueError(f"duplicate conflicting column {key}")
                    combined[key] = value
            rows.append(combined)
        max_ghi_diff = max(ghi_diffs)
        if max_ghi_diff > 1e-6:
            raise ValueError(f"GHI mismatch between source requests at {stem}: {max_ghi_diff}")
        path = out/f"{stem}_physical_weather_july2025.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        decision = assess_site(site["technology"], rows[0].keys())
        audit.append({
            "plant_id": site["plant_id"], "technology": site["technology"],
            "hours": len(rows), "max_ghi_request_disagreement_wm2": max_ghi_diff,
            "missing_weather_variables": decision["missing_weather_variables"],
            "missing_plant_parameters": decision["missing_plant_parameters"],
            "missing_independent_validation": decision["missing_independent_validation"],
            "physical_conversion_ready": decision["physical_conversion_ready"],
        })
    report = {
        "period": "2025-07", "sites": audit,
        "total_site_hours": sum(x["hours"] for x in audit),
        "meteorological_variable_requirements_met": all(not x["missing_weather_variables"] for x in audit),
        "physical_conversion_ready": all(x["physical_conversion_ready"] for x in audit),
        "renewable_availability_approved": False,
        "dispatch_approved": False,
    }
    (out/"manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("MERGED_PHYSICAL_WEATHER="+json.dumps(report, sort_keys=True))
    return report


if __name__ == "__main__":
    merge_site_weather("outputs/spatial_weather_pilot_2025",
                       "outputs/spatial_weather_extended_2025",
                       "outputs/spatial_weather_merged_2025")
