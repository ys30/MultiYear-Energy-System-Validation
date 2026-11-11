"""Independently reconcile original EIA-860 CISO OP rows against pinned totals.

This checks year-specific OP counts and nameplate MW only. It does not approve
BA mapping, generation availability, or empirical PyPSA dispatch.
"""
import argparse
import csv
import json
import math
from pathlib import Path

EXPECTED = {2024: (2645, 85634.2), 2025: (2786, 92530.0)}

def check(directory):
    directory = Path(directory)
    report = {"scope": "independent_original_workbook_op_inventory_check",
              "fleet_validated": False, "ba_mapping_validated": False,
              "empirical_dispatch_approved": False, "years": {}}
    for year, (expected_count, expected_mw) in EXPECTED.items():
        path = directory / f"eia860_ciso_generators_{year}.csv"
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        keys = [(r["plant_id_eia"].strip(), r["generator_id"].strip()) for r in rows]
        if len(set(keys)) != len(keys):
            raise ValueError(f"{year}: duplicate generator identity")
        op = [r for r in rows if r["status"].strip().upper() == "OP"]
        if not op:
            raise ValueError(f"{year}: no OP rows; verify original status encoding")
        capacity = []
        for r in op:
            value = float(r["nameplate_mw"])
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{year}: invalid OP nameplate {r}")
            capacity.append(value)
        total = round(math.fsum(capacity), 1)
        if len(op) != expected_count or abs(total - expected_mw) > 0.11:
            raise ValueError(f"{year}: independent OP count/MW {len(op)}/{total} "
                             f"does not match pinned {expected_count}/{expected_mw}")
        report["years"][str(year)] = {"op_count": len(op), "op_mw": total,
                                      "all_ciso_generator_rows": len(rows)}
    delta = round(report["years"]["2025"]["op_mw"] -
                  report["years"]["2024"]["op_mw"], 1)
    if abs(delta - 6895.8) > 0.11:
        raise ValueError(f"Independent net change mismatch: {delta}")
    report["op_delta_mw"] = delta
    report["original_workbook_op_totals_reconciled"] = True
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = check(args.extract_dir)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
