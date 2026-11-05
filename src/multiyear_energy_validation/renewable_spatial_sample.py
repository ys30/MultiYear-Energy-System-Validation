"""Capacity-weighted spatial sampling design for EIA-860 renewable plants.

Each technology is stratified by 1-degree latitude/longitude grid cells.
Select the largest plant per occupied cell, then fill a fixed site budget
by remaining plant capacity. This is a DESIGN diagnostic, not a validated
weather estimator or capacity coverage guarantee.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def spatial_sample_design(input_csv, output_json, per_technology=50, grid_degrees=1.0):
    if per_technology < 1 or not 0 < grid_degrees <= 5:
        raise ValueError("invalid sampling parameters")
    sites = defaultdict(float)
    with Path(input_csv).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            tech = row["technology"]
            if tech not in ("solar", "wind"):
                raise ValueError("unexpected technology")
            lat, lon, mw = float(row["latitude"]), float(row["longitude"]), float(row["capacity_mw"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180 and mw > 0):
                raise ValueError("invalid site record")
            sites[(tech, row["plant_id"], lat, lon)] += mw
    output = {"method": "one largest site per occupied 1-degree cell then largest remaining capacity",
              "grid_degrees": grid_degrees, "budget_per_technology": per_technology,
              "technology": {}, "sites": [],
              "weather_data_acquired": False, "regional_representativeness_approved": False,
              "renewable_availability_approved": False, "dispatch_approved": False}
    for tech in ("solar", "wind"):
        ranked = sorted(((key, mw) for key, mw in sites.items() if key[0] == tech),
                        key=lambda item: (-item[1], item[0][1]))
        cells = defaultdict(list)
        for key, mw in ranked:
            cell = (math.floor(key[2]/grid_degrees), math.floor(key[3]/grid_degrees))
            cells[cell].append((key, mw))
        mandatory = [entries[0] for entries in cells.values()]
        mandatory.sort(key=lambda item: (-item[1], item[0][1]))
        selected = mandatory[:per_technology]
        chosen = {item[0] for item in selected}
        for item in ranked:
            if len(selected) >= per_technology:
                break
            if item[0] not in chosen:
                selected.append(item)
                chosen.add(item[0])
        total_mw = sum(mw for _, mw in ranked)
        selected_mw = sum(mw for _, mw in selected)
        occupied = {(math.floor(k[2]/grid_degrees), math.floor(k[3]/grid_degrees)) for k, _ in selected}
        output["technology"][tech] = {
            "total_sites": len(ranked), "total_cells": len(cells),
            "selected_sites": len(selected), "selected_cells": len(occupied),
            "total_nameplate_mw": round(total_mw, 6),
            "selected_nameplate_mw": round(selected_mw, 6),
            "selected_capacity_fraction": round(selected_mw/total_mw, 6) if total_mw else 0,
            "spatial_cell_fraction": round(len(occupied)/len(cells), 6) if cells else 0,
            "all_cells_represented": len(occupied) == len(cells),
        }
        for (technology, plant_id, lat, lon), mw in selected:
            output["sites"].append({"technology": technology, "plant_id": plant_id,
                                    "latitude": lat, "longitude": lon, "nameplate_mw": round(mw, 6)})
    target = Path(output_json)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("SPATIAL_SAMPLE_DESIGN="+json.dumps({k:v for k,v in output.items() if k!="sites"},sort_keys=True))
    return output
