"""Solar site correlations after removing UTC-hour mean diurnal cycle.

The sample is a single month and two sites; these are screening statistics only.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


def _pearson(a, b):
    if len(a) < 3:
        return None
    ma, mb = mean(a), mean(b)
    sa, sb = pstdev(a), pstdev(b)
    if sa == 0 or sb == 0:
        return None
    return round(sum((x-ma)*(y-mb) for x,y in zip(a,b))/(len(a)*sa*sb), 6)


def solar_diurnal_anomalies(directory):
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    plants = [p for p in manifest["plants"] if p["technology"] == "solar"]
    if len(plants) != 2:
        raise ValueError("expected two solar sites")
    data = []
    for plant in plants:
        path = root / f"solar_plant_{plant['plant_id']}_july2025.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        data.append({r["period_utc"]: float(r["ghi_wm2"]) for r in rows})
    if len(data[0]) != 744 or set(data[0]) != set(data[1]):
        raise ValueError("incomplete or mismatched timestamps")
    hours = sorted(data[0])
    climatologies = []
    for site in data:
        by_hour = defaultdict(list)
        for timestamp in hours:
            by_hour[timestamp[11:13]].append(site[timestamp])
        climatologies.append({hour: mean(values) for hour, values in by_hour.items()})
    a = [data[0][t]-climatologies[0][t[11:13]] for t in hours]
    b = [data[1][t]-climatologies[1][t[11:13]] for t in hours]
    day = [i for i,t in enumerate(hours)
           if climatologies[0][t[11:13]] > 50 and climatologies[1][t[11:13]] > 50]
    result = {
        "period": "2025-07", "plant_ids": [p["plant_id"] for p in plants],
        "method": "subtract each site's July UTC-hour-of-day GHI mean",
        "all_hours": {"count": len(hours), "pearson_raw": _pearson([data[0][t] for t in hours], [data[1][t] for t in hours]),
                      "pearson_anomaly": _pearson(a,b)},
        "daytime_by_hourly_climatology_gt_50": {"count": len(day),
                      "pearson_anomaly": _pearson([a[i] for i in day],[b[i] for i in day])},
        "limitation": "hour-of-day detrending is not clear-sky-index normalization; only two sites and one month",
        "regional_inference_approved": False, "dispatch_approved": False,
    }
    (root/"solar_diurnal_anomaly.json").write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("SOLAR_DIURNAL_ANOMALY="+json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    solar_diurnal_anomalies("outputs/actual_plant_weather_month_2025")
