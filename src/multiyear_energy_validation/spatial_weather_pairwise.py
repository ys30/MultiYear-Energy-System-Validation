"""Six-site pairwise weather diagnostics using matched July UTC hours.

Raw and hour-of-day anomaly correlations are reported separately. This is
site-level weather evidence, not regional generation or power availability.
"""
import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev


def pearson(a, b):
    if len(a) != len(b) or len(a) < 3:
        raise ValueError("invalid paired time series")
    ma, mb = mean(a), mean(b)
    sa, sb = pstdev(a), pstdev(b)
    if sa == 0 or sb == 0:
        return None
    return round(sum((x-ma)*(y-mb) for x,y in zip(a,b))/(len(a)*sa*sb), 6)


def pairwise_spatial_weather(directory):
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    results = []
    for tech, variable in (("solar", "ghi_wm2"), ("wind", "wind_speed_10m_ms")):
        plants = [p for p in manifest["sites"] if p["technology"] == tech]
        if len(plants) != 3:
            raise ValueError("expected exactly three sites per technology")
        data = {}
        for plant in plants:
            path = root/f"{tech}_plant_{plant['plant_id']}_july2025.csv"
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            data[plant["plant_id"]] = {r["period_utc"]: float(r[variable]) for r in rows}
        hours = sorted(data[plants[0]["plant_id"]])
        if len(hours) != 744 or any(set(v) != set(hours) for v in data.values()):
            raise ValueError("missing or misaligned site hours")
        anomalies = {}
        for plant in plants:
            pid = plant["plant_id"]
            groups = defaultdict(list)
            for h in hours:
                groups[h[11:13]].append(data[pid][h])
            hourly_mean = {h: mean(v) for h,v in groups.items()}
            anomalies[pid] = [data[pid][h]-hourly_mean[h[11:13]] for h in hours]
        for a,b in combinations(plants,2):
            aid,bid = a["plant_id"],b["plant_id"]
            x = [data[aid][h] for h in hours]
            y = [data[bid][h] for h in hours]
            results.append({
                "technology": tech, "variable": variable,
                "plant_ids": [aid,bid], "hours": len(hours),
                "raw_pearson_r": pearson(x,y),
                "diurnal_anomaly_pearson_r": pearson(anomalies[aid],anomalies[bid]),
                "mean_absolute_hourly_difference": round(mean(abs(v-w) for v,w in zip(x,y)),6),
            })
    result = {
        "period": "2025-07",
        "method": "matched UTC-hour pairwise raw and site-specific hour-of-day anomaly correlations",
        "pairs": results,
        "sample_is_regionally_representative": False,
        "weather_to_power_conversion_validated": False,
        "dispatch_approved": False,
    }
    (root/"pairwise_weather_diagnostics.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("SPATIAL_WEATHER_PAIRWISE="+json.dumps(result,sort_keys=True))
    return result


if __name__ == "__main__":
    pairwise_spatial_weather("outputs/spatial_weather_pilot_2025")
