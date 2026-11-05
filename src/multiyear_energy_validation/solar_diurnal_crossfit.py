"""Out-of-sample diurnal anomaly correlation for two real solar sites.

Train hour-of-day means on odd calendar days, evaluate anomalies on even days,
and vice versa. This guards against estimating the hourly reference on the
same records used to evaluate correlation.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


def _corr(a, b):
    if len(a) < 3:
        raise ValueError("insufficient matched observations")
    ma, mb = mean(a), mean(b)
    sa, sb = pstdev(a), pstdev(b)
    if sa <= 0 or sb <= 0:
        raise ValueError("zero anomaly variance")
    return round(sum((x-ma)*(y-mb) for x, y in zip(a, b)) / (len(a)*sa*sb), 6)


def odd_even_crossfit(directory):
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    plants = [p for p in manifest["plants"] if p["technology"] == "solar"]
    if len(plants) != 2:
        raise ValueError("expected two solar plants")
    series = []
    for p in plants:
        path = root/f"solar_plant_{p['plant_id']}_july2025.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        series.append({r["period_utc"]: float(r["ghi_wm2"]) for r in rows})
    if len(series[0]) != 744 or set(series[0]) != set(series[1]):
        raise ValueError("incomplete matched July timestamps")
    times = sorted(series[0])
    folds = []
    for parity in (0, 1):
        train = [t for t in times if int(t[8:10]) % 2 != parity]
        test = [t for t in times if int(t[8:10]) % 2 == parity]
        reference = []
        for site in series:
            groups = defaultdict(list)
            for t in train:
                groups[t[11:13]].append(site[t])
            reference.append({h: mean(v) for h, v in groups.items()})
        a = [series[0][t]-reference[0][t[11:13]] for t in test]
        b = [series[1][t]-reference[1][t[11:13]] for t in test]
        daylight = [i for i,t in enumerate(test)
                    if reference[0][t[11:13]] > 50 and reference[1][t[11:13]] > 50]
        folds.append({
            "test_day_parity": "even" if parity == 0 else "odd",
            "train_hours": len(train), "test_hours": len(test),
            "test_anomaly_pearson_r": _corr(a, b),
            "test_daylight_hours": len(daylight),
            "test_daylight_anomaly_pearson_r": _corr([a[i] for i in daylight], [b[i] for i in daylight]),
        })
    result = {
        "period": "2025-07",
        "plant_ids": [p["plant_id"] for p in plants],
        "method": "cross-fitted UTC-hour climatology; odd/even calendar-day split",
        "folds": folds,
        "limitation": "odd/even split does not eliminate weather autocorrelation or establish regional representativeness",
        "regional_inference_approved": False,
        "dispatch_approved": False,
    }
    (root/"solar_diurnal_crossfit.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("SOLAR_DIURNAL_CROSSFIT="+json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    odd_even_crossfit("outputs/actual_plant_weather_month_2025")
