"""Summarize actual original-workbook bridge rows without relaxing acceptance gates."""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

def summarize(path):
    groups = defaultdict(lambda: {"count": 0, "delta_mw": 0.0, "rows": []})
    with Path(path).open(newline="") as stream:
        for row in csv.DictReader(stream):
            category = row["component"]
            old = row["status_2024"] or "<absent>"
            new = row["status_2025"] or "<absent>"
            delta = float(row["delta_mw"])
            if not math.isfinite(delta):
                raise ValueError("Nonfinite bridge delta")
            key = (category, old, new)
            group = groups[key]
            group["count"] += 1
            group["delta_mw"] += delta
            group["rows"].append({"plant_id_eia": row["plant_id_eia"],
                                  "generator_id": row["generator_id"],
                                  "delta_mw": delta})
    if not groups:
        raise ValueError("Empty bridge row artifact")
    breakdown = []
    for (category, old, new), group in sorted(groups.items()):
        breakdown.append({"component": category, "status_2024": old,
                          "status_2025": new, "generator_count": group["count"],
                          "delta_mw": round(group["delta_mw"], 4)})
    largest = sorted(
        ({"component": c, "status_2024": old, "status_2025": new, **row}
         for (c, old, new), group in groups.items() for row in group["rows"]),
        key=lambda row: abs(row["delta_mw"]), reverse=True)[:40]
    return {"scope": "official_extract_bridge_forensics_not_fleet_acceptance",
            "status_transition_breakdown": breakdown,
            "largest_absolute_capacity_changes": largest,
            "row_count": sum(x["generator_count"] for x in breakdown),
            "net_delta_mw": round(math.fsum(x["delta_mw"] for x in breakdown), 4),
            "archived_component_bridge_reconciled": False,
            "fleet_validated": False, "empirical_dispatch_approved": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bridge-rows", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = summarize(args.bridge_rows)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"row_count": report["row_count"],
                      "status_transition_breakdown": report["status_transition_breakdown"]}, indent=2))
