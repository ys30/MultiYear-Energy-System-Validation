"""Quantify inter-site hourly weather heterogeneity at actual EIA-860 plants.

Only observed NASA POWER point-weather statistics, not power production.
"""
import csv
import json
from pathlib import Path
from statistics import mean, pstdev


def analyze_month_weather(directory):
    root = Path(directory)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    by_tech = {}
    for tech in ("solar", "wind"):
        plants = [p for p in manifest["plants"] if p["technology"] == tech]
        if len(plants) != 2:
            raise ValueError("expected exactly two actual plants per technology")
        series = []
        for plant in plants:
            path = root / f"{tech}_plant_{plant['plant_id']}_july2025.csv"
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            series.append({row["period_utc"]: row for row in rows})
        if set(series[0]) != set(series[1]) or len(series[0]) != 744:
            raise ValueError("hourly time axes differ or incomplete")
        variable = "ghi_wm2" if tech == "solar" else "wind_speed_10m_ms"
        a = [float(series[0][hour][variable]) for hour in sorted(series[0])]
        b = [float(series[1][hour][variable]) for hour in sorted(series[0])]
        diffs = [x-y for x, y in zip(a, b)]
        am, bm = mean(a), mean(b)
        sd_a, sd_b = pstdev(a), pstdev(b)
        if sd_a == 0 or sd_b == 0:
            raise ValueError("zero variance in weather series")
        corr = sum((x-am)*(y-bm) for x,y in zip(a,b))/(len(a)*sd_a*sd_b)
        by_tech[tech] = {
            "plant_ids": [p["plant_id"] for p in plants],
            "variable": variable,
            "hours": len(a),
            "pearson_hourly_correlation": round(corr, 6),
            "mean_absolute_hourly_difference": round(mean(abs(x) for x in diffs), 6),
            "mean_signed_hourly_difference": round(mean(diffs), 6),
            "sample_coverage_fraction": manifest["capacity_coverage"][tech]["selected_capacity_fraction"],
        }
    result = {
        "period": "2025-07",
        "method": "matched UTC-hour NASA POWER site-pair differences",
        "technology": by_tech,
        "regional_inference_approved": False,
        "renewable_availability_approved": False,
        "dispatch_approved": False,
    }
    (root / "weather_heterogeneity.json").write_text(
        json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("ACTUAL_PLANT_HETEROGENEITY="+json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    analyze_month_weather("outputs/actual_plant_weather_month_2025")
