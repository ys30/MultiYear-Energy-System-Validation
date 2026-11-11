"""Validate checked-in 29-row PUDL cohort against archived EIA-860 transition JSON.

Usage:
  python scripts/verify_pudl_targets_against_artifact.py \
    --artifact /path/to/github-actions-artifact-13295023796.zip

This verifies EIA-860 input integrity, NOT PUDL matching.
"""
import argparse
import csv
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "data/pudl/project_a_pudl_29_targets.csv"

def check(artifact, targets=TARGETS):
    with zipfile.ZipFile(artifact) as z:
        names = [n for n in z.namelist()
                 if n.endswith("fleet_transitions_2024_2025.json")]
        if len(names) != 1:
            raise ValueError(f"Expected one fleet transition JSON, got {names}")
        transitions = json.loads(z.read(names[0]))
    source = {}
    for x in transitions["changes"]:
        if x.get("classification") != "new_to_ciso_inventory":
            continue
        year = x.get("current_operating_year_raw")
        if year is None or int(year) >= 2025:
            continue
        key = (str(x["plant_id"]).strip(), str(x["generator_id"]).strip())
        if key in source:
            raise ValueError(f"Duplicate source key {key}")
        source[key] = x
    with open(targets, newline="") as f:
        csv_rows = list(csv.DictReader(f))
    if len(csv_rows) != 29 or len(source) != 29:
        raise ValueError(f"Unexpected counts: CSV={len(csv_rows)} source={len(source)}")
    seen = set()
    op_mw = 0.0
    for row in csv_rows:
        key = (row["plant_id_eia"].strip(), row["generator_id"].strip())
        if key in seen or key not in source:
            raise ValueError(f"Duplicate or absent source key {key}")
        seen.add(key)
        x = source[key]
        if row["status_2025"] != x["current_status"]:
            raise ValueError(f"Status mismatch {key}")
        if int(row["reported_operating_year"]) != int(x["current_operating_year_raw"]):
            raise ValueError(f"Operating year mismatch {key}")
        expected = float(x["current_nameplate_mw"]) if x["current_status"] == "OP" else 0.0
        actual = float(row["op_nameplate_mw_2025"])
        if abs(actual - expected) > 1e-6:
            raise ValueError(f"OP capacity mismatch {key}: {actual} vs {expected}")
        op_mw += actual
    if set(source) != seen or abs(op_mw - 138.1) > 1e-6:
        raise ValueError("Source/CSV key set or OP capacity mismatch")
    result = {"records": len(seen), "op_mw": round(op_mw, 1),
              "source": "archived_eia860_transitions",
              "pudl_matched": False, "empirical_dispatch_approved": False}
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--targets", default=str(TARGETS))
    args = parser.parse_args()
    check(args.artifact, args.targets)
