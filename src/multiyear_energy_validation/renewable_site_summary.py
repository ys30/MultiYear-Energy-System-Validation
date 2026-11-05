"""Summarize geocoded CISO renewable generators by technology and plant.

This does not estimate weather or available generation.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path


def summarize_geocoded(csv_path, destination):
    totals = defaultdict(float)
    generator_counts = defaultdict(int)
    plants = defaultdict(set)
    sites = defaultdict(lambda: {"capacity_mw": 0.0, "generator_count": 0})
    with Path(csv_path).open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            tech = row["technology"]
            if tech not in ("solar", "wind"):
                raise ValueError("unexpected technology")
            mw = float(row["capacity_mw"])
            if mw <= 0:
                raise ValueError("invalid capacity")
            totals[tech] += mw
            generator_counts[tech] += 1
            plants[tech].add(row["plant_id"])
            key = (tech, row["plant_id"], row["latitude"], row["longitude"])
            sites[key]["capacity_mw"] += mw
            sites[key]["generator_count"] += 1
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "technology": {tech: {
            "generator_count": generator_counts[tech],
            "plant_count": len(plants[tech]),
            "nameplate_mw": round(totals[tech], 6),
        } for tech in ("solar", "wind")},
        "unique_plant_weather_sites": len(sites),
        "capacity_weighted_weather_ready": False,
        "weather_data_ingested": False,
        "dispatch_approved": False,
    }
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("EIA860_RENEWABLE_TECH=" + json.dumps(result, sort_keys=True))
    return result
