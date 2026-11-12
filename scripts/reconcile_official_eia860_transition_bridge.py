"""Decompose year-on-year CISO OP nameplate changes by generator identity.

Reads *original-workbook staging extracts*; expected components are independently
pinned from the archived transition audit. A pass checks numerical agreement,
not plant BA certification or empirical PyPSA dispatch readiness.
"""
import argparse
import csv
import json
import math
from pathlib import Path

EXPECTED = {
    "new_to_inventory": 6339.3,
    "missing_from_inventory": -379.9,
    "status_transitions": 862.4,
    "nameplate_revisions": 74.0,
    "net_change": 6895.8,
}

def load(path):
    result = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["plant_id_eia"].strip(), row["generator_id"].strip())
            if key in result:
                raise ValueError(f"Duplicate generator key: {key}")
            status = row["status"].strip().upper()
            raw = row["nameplate_mw"]
            if status == "OP" and raw in ("", None):
                raise ValueError(f"Missing OP nameplate for {key}")
            mw = float(raw) if raw not in ("", None) else 0.0
            if not math.isfinite(mw) or mw < 0:
                raise ValueError(f"Invalid nameplate for {key}: {raw}")
            result[key] = (status, mw)
    if not result:
        raise ValueError(f"Empty generator extract: {path}")
    return result

def decompose(directory):
    directory = Path(directory)
    before = load(directory / "eia860_ciso_generators_2024.csv")
    after = load(directory / "eia860_ciso_generators_2025.csv")
    components = {key: [] for key in EXPECTED if key != "net_change"}
    for key in sorted(set(before) | set(after)):
        old = before.get(key)
        new = after.get(key)
        old_mw = old[1] if old and old[0] == "OP" else 0.0
        new_mw = new[1] if new and new[0] == "OP" else 0.0
        delta = new_mw - old_mw
        if key not in before:
            category = "new_to_inventory"
        elif key not in after:
            category = "missing_from_inventory"
        elif old[0] != new[0]:
            category = "status_transitions"
        else:
            category = "nameplate_revisions"
        if delta:
            components[category].append({"plant_id_eia": key[0],
                                         "generator_id": key[1],
                                         "delta_mw": round(delta, 5)})
    totals = {category: round(math.fsum(x["delta_mw"] for x in rows), 1)
              for category, rows in components.items()}
    totals["net_change"] = round(math.fsum(totals.values()), 1)
    direct_delta = round(
        math.fsum(mw for status, mw in after.values() if status == "OP") -
        math.fsum(mw for status, mw in before.values() if status == "OP"), 1)
    if abs(totals["net_change"] - direct_delta) > 0.11:
        raise ValueError(f"Bridge arithmetic mismatch: {totals['net_change']} vs {direct_delta}")
    checks = {k: abs(totals[k] - expected) <= 0.11 for k, expected in EXPECTED.items()}
    report = {"scope": "original_workbook_generator_identity_bridge",
              "components_mw": totals, "expected_mw": EXPECTED,
              "component_checks": checks,
              "component_counts_nonzero": {k: len(v) for k, v in components.items()},
              "bridge_reconciled": all(checks.values()),
              "ba_mapping_validated": False,
              "empirical_dispatch_approved": False}
    return report, components

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report, components = decompose(args.extract_dir)
    detail_path = Path(args.output).with_name("independent-transition-bridge-rows.csv")
    with detail_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["component", "plant_id_eia", "generator_id", "delta_mw"])
        writer.writeheader()
        for category, rows in components.items():
            for row in rows:
                writer.writerow({"component": category, **row})
    report["row_level_artifact"] = detail_path.name
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["bridge_reconciled"]:
        raise SystemExit("Original-workbook component bridge differs from archived benchmark")
