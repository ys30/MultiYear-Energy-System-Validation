"""Fail-closed official EIA860 2025 target metadata validation."""
import argparse
import csv
import json
from pathlib import Path


def verify(official, targets):
    records = [r for r in official["target_year_records"] if r["year"] == 2025]
    by_key = {(r["plant_id_eia"], r["generator_id"]): r for r in records}
    if len(records) != 29 or len(by_key) != 29:
        raise ValueError("Expected 29 distinct official 2025 keys")
    with open(targets, newline="", encoding="utf-8-sig") as f:
        target_rows = list(csv.DictReader(f))
    if len(target_rows) != 29:
        raise ValueError("Expected 29 target rows")
    mismatches = []
    for t in target_rows:
        key = (int(t["plant_id_eia"]), t["generator_id"].strip())
        row = by_key.get(key)
        if row is None or not row["exact_match"]:
            mismatches.append({"key": key, "reason": "missing official exact record"})
            continue
        metadata = row.get("official_selected_metadata", [])
        if len(metadata) != 1:
            mismatches.append({"key": key, "reason": "ambiguous official records"})
            continue
        values = metadata[0]["fields"]
        if str(values.get("Operating Year", "")).strip() != str(int(t["reported_operating_year"])):
            mismatches.append({"key": key, "field": "Operating Year"})
        if str(values.get("Status", "")).strip() != t["status_2025"].strip():
            mismatches.append({"key": key, "field": "Status"})
        if t["status_2025"].strip() == "OP":
            try:
                capacity = float(str(values["Nameplate Capacity (MW)"]).strip())
                target_capacity = float(t["op_nameplate_mw_2025"])
                if abs(capacity - target_capacity) > 0.0001:
                    mismatches.append({"key": key, "field": "OP Nameplate Capacity"})
            except (KeyError, ValueError, TypeError):
                mismatches.append({"key": key, "field": "OP Nameplate Capacity unreadable"})
    if mismatches:
        raise ValueError("Official EIA860 target metadata mismatches: " + json.dumps(mismatches))
    return {"target_keys_checked": 29, "metadata_mismatches": 0,
            "checked_fields": ["Operating Year", "Status", "OP Nameplate Capacity (MW)"],
            "generator_identity_crosswalk_verified": False,
            "physical_commissioning_verified": False,
            "empirical_dispatch_approved": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--official-json", required=True)
    p.add_argument("--targets", default="data/pudl/project_a_pudl_29_targets.csv")
    a = p.parse_args()
    result = verify(json.loads(Path(a.official_json).read_text()), a.targets)
    print("OFFICIAL_EIA860_TARGET_METADATA_VERIFIED=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
