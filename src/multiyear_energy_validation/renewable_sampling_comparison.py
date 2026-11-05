"""Compare capacity-only and geographic-stratified renewable site selection.

Both approaches use the same number of real EIA-860 plant locations.
This is a coverage diagnostic, not a validation of weather representativeness.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from .renewable_spatial_sample import spatial_sample_design


def compare_sampling(input_csv, output_json, budget=50, grid_degrees=1.0):
    target = Path(output_json)
    spatial = spatial_sample_design(input_csv, target.with_name("spatial_selection_details.json"), budget, grid_degrees)
    sites = defaultdict(float)
    with Path(input_csv).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row["technology"], row["plant_id"], float(row["latitude"]), float(row["longitude"]))
            sites[key] += float(row["capacity_mw"])
    comparison = {}
    for tech in ("solar", "wind"):
        ranked = sorted(((key, mw) for key, mw in sites.items() if key[0] == tech),
                        key=lambda item: (-item[1], item[0][1]))
        selected = ranked[:budget]
        total_mw = sum(mw for _, mw in ranked)
        all_cells = {(math.floor(k[2]/grid_degrees), math.floor(k[3]/grid_degrees)) for k, _ in ranked}
        selected_cells = {(math.floor(k[2]/grid_degrees), math.floor(k[3]/grid_degrees)) for k, _ in selected}
        comparison[tech] = {
            "capacity_only": {
                "selected_sites": len(selected),
                "capacity_fraction": round(sum(mw for _, mw in selected)/total_mw, 6),
                "selected_cells": len(selected_cells),
                "cell_fraction": round(len(selected_cells)/len(all_cells), 6),
            },
            "spatial_stratified": {
                "selected_sites": spatial["technology"][tech]["selected_sites"],
                "capacity_fraction": spatial["technology"][tech]["selected_capacity_fraction"],
                "selected_cells": spatial["technology"][tech]["selected_cells"],
                "cell_fraction": spatial["technology"][tech]["spatial_cell_fraction"],
            },
        }
    result = {
        "budget_per_technology": budget, "grid_degrees": grid_degrees,
        "technology": comparison, "weather_representativeness_approved": False,
        "dispatch_approved": False,
    }
    target.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("RENEWABLE_SAMPLING_COMPARISON="+json.dumps(result, sort_keys=True))
    return result
