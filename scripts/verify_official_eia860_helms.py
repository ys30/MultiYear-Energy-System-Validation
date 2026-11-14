"""Independent original-workbook check for Helms OA-to-OP transitions.

This narrow audit does not validate the entire fleet or BA mapping.
"""
import argparse
import csv
import json
from pathlib import Path

PLANT = "6100"
GENERATORS = ("1", "2", "3")
EXPECTED_MW = 351.0


def read_rows(path):
    with open(path, newline="") as stream:
        rows = list(csv.DictReader(stream))
    matches = {}
    for row in rows:
        if row["plant_id_eia"].strip() != PLANT:
            continue
        gid = row["generator_id"].strip()
        if gid in matches:
            raise ValueError(f"Duplicate Helms generator {gid}")
        matches[gid] = row
    return matches


def verify(directory):
    directory = Path(directory)
    before = read_rows(directory / "eia860_ciso_generators_2024.csv")
    after = read_rows(directory / "eia860_ciso_generators_2025.csv")
    result = []
    for gid in GENERATORS:
        if gid not in before or gid not in after:
            raise ValueError(f"Helms generator {gid} missing from CISO extract")
        old, new = before[gid], after[gid]
        statuses = (old["status"].strip().upper(), new["status"].strip().upper())
        capacities = (float(old["nameplate_mw"]), float(new["nameplate_mw"]))
        if statuses != ("OA", "OP"):
            raise ValueError(f"Helms generator {gid} unexpected statuses: {statuses}")
        if any(abs(x - EXPECTED_MW) > 0.01 for x in capacities):
            raise ValueError(f"Helms generator {gid} unexpected nameplate: {capacities}")
        result.append({"plant_id_eia": PLANT, "generator_id": gid,
                       "status_2024": statuses[0], "status_2025": statuses[1],
                       "nameplate_mw_2024": capacities[0],
                       "nameplate_mw_2025": capacities[1],
                       "op_delta_mw": EXPECTED_MW})
    return {"scope": "helms_original_workbook_transition_only",
            "helms_generator_count": len(result), "helms_op_delta_mw": sum(x["op_delta_mw"] for x in result),
            "helms_transition_reconciled": True, "generators": result,
            "fleet_validated": False, "ba_mapping_validated": False,
            "empirical_dispatch_approved": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = verify(args.extract_dir)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
