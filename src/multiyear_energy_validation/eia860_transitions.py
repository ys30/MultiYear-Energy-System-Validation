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
    operating_year_counts = Counter()
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
        if kind in ("new_to_ciso_inventory", "missing_from_ciso_inventory"):
            source = b if b is not None else a
            raw = str(source.get("operating_year_raw") or "").strip()
            try:
                year = int(float(raw))
                if not 1850 <= year <= 2100 or float(raw) != year:
                    raise ValueError(raw)
                bucket = str(year)
            except (ValueError, TypeError, OverflowError):
                bucket = "missing_or_invalid"
            operating_year_counts[(kind, source["technology"], bucket)] += 1
        if kind != "unchanged":
            changes.append({
                "plant_id": key[0], "generator_id": key[1], "classification": kind,
                "previous_status": a["status_raw"] if a else None,
                "current_status": b["status_raw"] if b else None,
                "previous_technology": a["technology"] if a else None,
                "current_technology": b["technology"] if b else None,
                "previous_operating_year_raw": a.get("operating_year_raw") if a else None,
                "current_operating_year_raw": b.get("operating_year_raw") if b else None,
                "previous_operating_month_raw": a.get("operating_month_raw") if a else None,
                "current_operating_month_raw": b.get("operating_month_raw") if b else None,
                "previous_nameplate_mw": a["mw"] if a else 0.0,
                "current_nameplate_mw": b["mw"] if b else 0.0,
            })
    def op_mw(records):
        return sum(r["mw"] for r in records.values() if r["status_raw"] == "OP")
    delta = op_mw(new) - op_mw(old)
    components = Counter()
    technology_components = Counter()
    technology_transition_counts = Counter()
    status_transition_counts = Counter()
    status_transition_op_delta_mw = Counter()
    for row in changes:
        before = row["previous_nameplate_mw"] if row["previous_status"] == "OP" else 0.0
        after = row["current_nameplate_mw"] if row["current_status"] == "OP" else 0.0
        components[row["classification"]] += after - before
        if row["classification"] == "status_changed":
            transition = (row["previous_status"], row["current_status"], row["current_technology"])
            status_transition_counts[transition] += 1
            status_transition_op_delta_mw[transition] += after - before
        if before:
            technology_components[row["previous_technology"]] -= before
        if after:
            technology_components[row["current_technology"]] += after
        technology_transition_counts[(row["classification"], row["current_technology"] or row["previous_technology"])] += 1
    if abs(sum(components.values()) - delta) > 1e-5:
        raise AssertionError("OP capacity reconciliation failed")
    if abs(sum(technology_components.values()) - delta) > 1e-5:
        raise AssertionError("technology OP capacity reconciliation failed")
    if abs(sum(status_transition_op_delta_mw.values()) - components["status_changed"]) > 1e-5:
        raise AssertionError("status transition OP capacity reconciliation failed")
    report = {
        "scope": "CISO EIA-860 annual inventory; identity match is not proof of physical commissioning/retirement",
        "previous_rows": len(old), "current_rows": len(new),
        "classification_counts": dict(sorted(categories.items())),
        "op_previous_nameplate_mw": op_mw(old),
        "op_current_nameplate_mw": op_mw(new),
        "op_delta_nameplate_mw": delta,
        "op_delta_by_classification_mw": dict(sorted(components.items())),
        "op_delta_by_technology_mw": dict(sorted(technology_components.items())),
        "transition_counts_by_classification_and_technology": [
            {"classification": classification, "technology": technology, "count": count}
            for (classification, technology), count in sorted(technology_transition_counts.items())
        ],
        "status_transitions_by_technology": [
            {"previous_status": previous, "current_status": current, "technology": technology,
             "count": status_transition_counts[(previous, current, technology)],
             "op_delta_nameplate_mw": status_transition_op_delta_mw[(previous, current, technology)]}
            for previous, current, technology in sorted(status_transition_counts)
        ],
        "inventory_membership_operating_year_counts": [
            {"classification": classification, "technology": technology,
             "reported_operating_year": year, "count": count}
            for (classification, technology, year), count in sorted(operating_year_counts.items())
        ],
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
