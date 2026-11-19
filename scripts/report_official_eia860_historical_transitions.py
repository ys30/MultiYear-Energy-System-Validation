"""Summarize official annual generator transitions without inferring physical events."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def build_report(audit):
    rows = audit["historical_four_plant_records"]
    grouped = defaultdict(dict)
    for r in rows:
        year = int(r["year"])
        if year not in (2023, 2024):
            raise ValueError(f"Unexpected historical year: {year}")
        key = (int(r["plant_id_eia"]), str(r["generator_id"]))
        if year in grouped[key]:
            raise ValueError(f"Duplicate official generator record: {key} {year}")
        grouped[key][year] = r
    changes = []
    for (plant, generator), annual in sorted(grouped.items()):
        if set(annual) != {2023, 2024}:
            raise ValueError(f"Incomplete historical source for {plant}/{generator}: {sorted(annual)}")
        before = annual[2023]["fields"]
        after = annual[2024]["fields"]
        fields = ["Status", "Nameplate Capacity (MW)", "Operating Year", "Operating Month"]
        missing = [field for field in fields if field not in before or field not in after]
        if missing:
            raise ValueError(f"Missing required official fields for {plant}/{generator}: {missing}")
        changed = {field: {"2023": before[field], "2024": after[field]}
                   for field in fields if before[field] != after[field]}
        changes.append({"plant_id_eia": plant, "generator_id": generator,
                        "official_2023_sheet": annual[2023]["sheet"],
                        "official_2024_sheet": annual[2024]["sheet"],
                        "changed_fields": changed,
                        "retirement_2023": {k: v for k, v in before.items() if k.startswith("Retirement")},
                        "retirement_2024": {k: v for k, v in after.items() if k.startswith("Retirement")},
                        "physical_event_inferred": False})
    return {"source": "official_EIA860_annual", "historical_generator_keys": len(changes),
            "changed_generator_keys": sum(bool(x["changed_fields"]) for x in changes),
            "records": changes, "generator_identity_crosswalk_verified": False,
            "physical_commissioning_verified": False, "empirical_dispatch_approved": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audit-json", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    report = build_report(json.loads(Path(args.audit_json).read_text()))
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("OFFICIAL_HISTORICAL_TRANSITIONS=" + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
