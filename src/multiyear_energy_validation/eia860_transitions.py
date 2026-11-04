"""Compare two annual EIA-860 CISO fleet snapshots by plant/generator ID.

Screening-only accounting; neither nameplate MW nor OP status implies hourly availability.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def _read(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        key = (row["plant_id"].strip(), row["generator_id"].strip())
        if not all(key) or key in result:
            raise ValueError(f"empty or duplicate plant/generator ID: {key}")
        mw = float(row["nameplate_capacity_mw"])
        if not (0 < mw < float("inf")):
            raise ValueError(f"invalid nameplate capacity for {key}")
        result[key] = {**row, "mw": mw}
    return result


def compare(previous_csv, current_csv, output_json):
    old, new = _read(previous_csv), _read(current_csv)
    categories = Counter()
    changes = []
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        if a is None:
            kind = "new_to_ciso_inventory"
        elif b is None:
            kind = "missing_from_ciso_inventory"
        elif a["status_raw"] != b["status_raw"]:
            kind = "status_changed"
        elif a["technology"] != b["technology"]:
            kind = "technology_changed"
        elif abs(a["mw"] - b["mw"]) > 1e-6:
            kind = "nameplate_changed"
        else:
            kind = "unchanged"
        categories[kind] += 1
        if kind != "unchanged":
            changes.append({
                "plant_id": key[0], "generator_id": key[1], "classification": kind,
                "previous_status": a["status_raw"] if a else None,
                "current_status": b["status_raw"] if b else None,
                "previous_technology": a["technology"] if a else None,
                "current_technology": b["technology"] if b else None,
                "previous_nameplate_mw": a["mw"] if a else 0.0,
                "current_nameplate_mw": b["mw"] if b else 0.0,
            })
    def op_mw(records):
        return sum(r["mw"] for r in records.values() if r["status_raw"] == "OP")
    delta = op_mw(new) - op_mw(old)
    components = Counter()
    for row in changes:
        before = row["previous_nameplate_mw"] if row["previous_status"] == "OP" else 0.0
        after = row["current_nameplate_mw"] if row["current_status"] == "OP" else 0.0
        components[row["classification"]] += after - before
    if abs(sum(components.values()) - delta) > 1e-5:
        raise AssertionError("OP capacity reconciliation failed")
    report = {
        "scope": "CISO EIA-860 annual inventory; identity match is not proof of physical commissioning/retirement",
        "previous_rows": len(old), "current_rows": len(new),
        "classification_counts": dict(sorted(categories.items())),
        "op_previous_nameplate_mw": op_mw(old),
        "op_current_nameplate_mw": op_mw(new),
        "op_delta_nameplate_mw": delta,
        "op_delta_by_classification_mw": dict(sorted(components.items())),
        "changes": changes,
        "empirical_dispatch_ready": False,
    }
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = compare(args.previous, args.current, args.output)
    print("EIA860_FLEET_TRANSITIONS=" + json.dumps(
        {k: v for k, v in result.items() if k != "changes"}, sort_keys=True))
