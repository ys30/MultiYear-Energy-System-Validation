"""Rank actual CISO renewable plant locations by nameplate MW for bounded weather sampling."""
import csv
import json
from collections import defaultdict
from pathlib import Path


def select_weather_sites(input_csv, output_json, per_technology=10):
    if per_technology < 1:
        raise ValueError("per_technology must be positive")
    sites = defaultdict(float)
    totals = defaultdict(float)
    with Path(input_csv).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            tech = row["technology"]
            if tech not in ("solar", "wind"):
                raise ValueError("unknown technology")
            mw = float(row["capacity_mw"])
            if mw <= 0:
                raise ValueError("non-positive capacity")
            key = (tech, row["plant_id"], row["latitude"], row["longitude"])
            sites[key] += mw
            totals[tech] += mw
    selected = []
    coverage = {}
    for tech in ("solar", "wind"):
        ranked = sorted(((key, mw) for key, mw in sites.items() if key[0] == tech),
                        key=lambda item: (-item[1], item[0][1]))
        chosen = ranked[:per_technology]
        chosen_mw = sum(mw for _, mw in chosen)
        coverage[tech] = {
            "total_nameplate_mw": round(totals[tech], 6),
            "selected_nameplate_mw": round(chosen_mw, 6),
            "selected_capacity_fraction": round(chosen_mw / totals[tech], 6) if totals[tech] else 0,
            "total_sites": len(ranked), "selected_sites": len(chosen),
        }
        for (technology, plant_id, lat, lon), mw in chosen:
            selected.append({"technology": technology, "plant_id": plant_id,
                             "latitude": float(lat), "longitude": float(lon),
                             "nameplate_mw": round(mw, 6)})
    result = {
        "selection_method": "top nameplate capacity sites per technology",
        "per_technology": per_technology,
        "coverage": coverage, "selected_sites": selected,
        "selection_is_not_representative": True,
        "weather_observations_acquired": False,
        "renewable_availability_approved": False,
        "dispatch_approved": False,
    }
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("RENEWABLE_SITE_SELECTION=" + json.dumps({k: v for k, v in result.items() if k != "selected_sites"}, sort_keys=True))
    return result
