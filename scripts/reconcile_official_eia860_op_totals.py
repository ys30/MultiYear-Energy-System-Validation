"""Independently reconcile original EIA-860 CISO OP rows against pinned totals.

This checks year-specific OP counts and nameplate MW only. It does not approve
BA mapping, generation availability, or empirical PyPSA dispatch.
"""
import argparse
import csv
import json
import math
from itertools import combinations
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
        # Diagnostic only: test whether a different status denominator reproduces
        # the archived row count. Never use it to override the OP acceptance gate.
        status_counts = {status: sum(row["status"].strip().upper() == status for row in rows)
                         for status in sorted(set(row["status"].strip().upper() for row in rows))}
        other_statuses = [status for status in status_counts if status != "OP"]
        denominator_candidates = []
        for n in range(1, min(4, len(other_statuses)) + 1):
            for subset in combinations(other_statuses, n):
                candidate_count = len(op) + sum(status_counts[status] for status in subset)
                if candidate_count == expected_count:
                    denominator_candidates.append({
                        "included_statuses": ["OP", *subset],
                        "row_count": candidate_count,
                        "interpretation": "count_match_only_not_validated_op_definition",
                    })
        operable_statuses = ("OP", "OA", "OS", "SB")
        operable_count = sum(status_counts.get(status, 0) for status in operable_statuses)
        report["years"][str(year)] = {
            "op_count": len(op), "op_mw": total,
            "all_ciso_generator_rows": len(rows),
            "pinned_op_count": expected_count, "pinned_op_mw": expected_mw,
            "op_count_difference": len(op) - expected_count,
            "op_mw_difference": round(total - expected_mw, 1),
            "zero_mw_op_count": sum(mw == 0 for mw in capacity),
            "status_counts": status_counts,
            "alternative_denominator_count_matches": denominator_candidates,
            "operable_status_set": list(operable_statuses),
            "operable_status_count": operable_count,
            "operable_count_matches_pinned": operable_count == expected_count,
            "operable_status_count_is_verified_archived_definition": False,
            "alternative_denominator_is_acceptance": False,
            "source_sheet_op_counts": {sheet: sum(row["status"].strip().upper() == "OP" and
                                             row.get("source_sheet", "") == sheet for row in rows)
                                       for sheet in sorted(set(row.get("source_sheet", "") for row in rows))},
            "count_matches_pinned": len(op) == expected_count,
            "mw_matches_pinned": abs(total - expected_mw) <= 0.11,
        }
    delta = round(report["years"]["2025"]["op_mw"] -
                  report["years"]["2024"]["op_mw"], 1)
    if abs(delta - 6895.8) > 0.11:
        raise ValueError(f"Independent net change {delta} does not match pinned 6895.8")
    report["op_delta_mw"] = delta
    report["both_years_operable_count_matches_pinned"] = all(
        info["operable_count_matches_pinned"] for info in report["years"].values())
    report["original_workbook_op_totals_reconciled"] = all(
        row["count_matches_pinned"] and row["mw_matches_pinned"]
        for row in report["years"].values())
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = check(args.extract_dir)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["original_workbook_op_totals_reconciled"]:
        raise SystemExit("Official OP inventory differs from archived count/MW benchmark; see diagnostic JSON")
