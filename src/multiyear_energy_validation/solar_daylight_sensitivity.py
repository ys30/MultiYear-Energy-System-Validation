"""Daylight-conditioned solar weather comparison at real CISO plant sites.

Screening only: daylight threshold is applied to both sites, with a sensitivity
grid. This removes shared nighttime zeros but does not remove solar geometry.
"""
import csv
import json
from pathlib import Path
from statistics import mean, pstdev


def _corr(x, y):
    if len(x) < 3:
        return None
    ax, ay = mean(x), mean(y)
    sx, sy = pstdev(x), pstdev(y)
    if sx == 0 or sy == 0:
        return None
    return round(sum((a-ax)*(b-ay) for a,b in zip(x,y))/(len(x)*sx*sy), 6)


def daylight_sensitivity(directory, thresholds=(0, 50, 200)):
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    plants = [p for p in manifest["plants"] if p["technology"] == "solar"]
    if len(plants) != 2:
        raise ValueError("expected two solar sites")
    series = []
    for p in plants:
        with (root/f"solar_plant_{p['plant_id']}_july2025.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        series.append({r["period_utc"]: float(r["ghi_wm2"]) for r in rows})
    if set(series[0]) != set(series[1]) or len(series[0]) != 744:
        raise ValueError("mismatched hourly time axis")
    hours = sorted(series[0])
    out = []
    for threshold in thresholds:
        paired = [(series[0][h], series[1][h]) for h in hours
                  if series[0][h] > threshold and series[1][h] > threshold]
        a, b = [x for x,_ in paired], [y for _,y in paired]
        out.append({"both_sites_ghi_gt_wm2": threshold,
                    "matched_hours": len(paired),
                    "pearson_r": _corr(a,b),
                    "mean_absolute_difference_wm2": round(mean(abs(x-y) for x,y in paired), 6) if paired else None})
    result = {"period": "2025-07", "plant_ids": [p["plant_id"] for p in plants],
              "method": "same-hour pairwise GHI threshold at both sites",
              "threshold_sensitivity": out,
              "shared_solar_geometry_not_removed": True,
              "regional_inference_approved": False,
              "dispatch_approved": False}
    (root/"solar_daylight_sensitivity.json").write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("SOLAR_DAYLIGHT_SENSITIVITY="+json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    daylight_sensitivity("outputs/actual_plant_weather_month_2025")
