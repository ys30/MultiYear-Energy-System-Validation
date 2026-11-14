"""Cross-check archived 29-entrant cohort identities/statuses against official extracts.

Operating-year fields are NOT present in these extracts and are NOT verified.
"""
import argparse
import csv
import json
from pathlib import Path

TARGETS = Path(__file__).resolve().parents[1] / "data/pudl/project_a_pudl_29_targets.csv"


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    result = {}
    for row in rows:
        key = (row["plant_id_eia"].strip(), row["generator_id"].strip())
        if not all(key) or key in result:
            raise ValueError(f"Invalid or duplicate generator key: {key}")
        result[key] = row
    return result


def verify(extract_dir, targets=TARGETS):
    root = Path(extract_dir)
    before = load(root / "eia860_ciso_generators_2024.csv")
    after = load(root / "eia860_ciso_generators_2025.csv")
    cohort = load(targets)
    if len(cohort) != 29:
        raise ValueError(f"Expected 29 archived cohort records, got {len(cohort)}")
    total = 0.0
    for key, target in cohort.items():
        if key in before:
            raise ValueError(f"Archived entrant already in 2024 official inventory: {key}")
        if key not in after:
            raise ValueError(f"Archived entrant absent from 2025 official inventory: {key}")
        observed = after[key]
        status = observed["status"].strip().upper()
        if status != target["status_2025"].strip().upper():
            raise ValueError(f"Status mismatch for {key}: {status}")
        observed_mw = float(observed["nameplate_mw"]) if status == "OP" else 0.0
        expected_mw = float(target["op_nameplate_mw_2025"])
        if abs(observed_mw - expected_mw) > 0.01:
            raise ValueError(f"OP capacity mismatch for {key}: {observed_mw} vs {expected_mw}")
        total += observed_mw
    if abs(total - 138.1) > 0.01:
        raise ValueError(f"29-record OP total mismatch: {total}")
    return {"scope": "29_archived_entrant_keys_status_and_op_capacity_only",
            "official_extracts_crosschecked": True,
            "record_count": len(cohort), "op_capacity_mw": round(total, 1),
            "operating_year_independently_verified": False,
            "pudl_matched": False, "fleet_validated": False,
            "ba_mapping_validated": False, "empirical_dispatch_approved": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-dir", required=True)
    parser.add_argument("--targets", default=str(TARGETS))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = verify(args.extract_dir, args.targets)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
