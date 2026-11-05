"""Capacity-coverage sensitivity for CISO renewable plant weather sampling.

This is a sample-size diagnostic, not a representative weather estimator.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path


def capacity_coverage_curve(input_csv, output_json, thresholds=(0.5, 0.75, 0.9, 0.95)):
    sites = defaultdict(float)
    for row in csv.DictReader(Path(input_csv).open(newline="", encoding="utf-8")):
        technology = row["technology"]
        if technology not in ("solar", "wind"):
            raise ValueError("unknown renewable technology")
        mw = float(row["capacity_mw"])
        if mw <= 0:
            raise ValueError("invalid MW")
        sites[(technology, row["plant_id"], row["latitude"], row["longitude"])] += mw
    result = {"method": "descending nameplate capacity, separate technology",
              "thresholds": {}, "representative_weather_approved": False,
              "dispatch_approved": False}
    for tech in ("solar", "wind"):
        ranked = sorted((mw for (t, *_), mw in sites.items() if t == tech), reverse=True)
        total = sum(ranked)
        if not ranked or total <= 0:
            raise ValueError("no eligible sites")
        cumulative = 0.0
        threshold_rows = []
        targets = sorted(thresholds)
        target_index = 0
        for index, mw in enumerate(ranked, 1):
            cumulative += mw
            while target_index < len(targets) and cumulative / total + 1e-12 >= targets[target_index]:
                threshold_rows.append({
                    "target_fraction": targets[target_index],
                    "minimum_top_sites": index,
                    "achieved_fraction": round(cumulative / total, 6),
                })
                target_index += 1
        result["thresholds"][tech] = {
            "total_sites": len(ranked), "total_nameplate_mw": round(total, 6),
            "minimum_sites_by_coverage": threshold_rows,
        }
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RENEWABLE_COVERAGE_CURVE=" + json.dumps(result, sort_keys=True))
    return result
