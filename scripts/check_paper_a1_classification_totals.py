"""Fail closed unless E1.2 categories sum to the E1.1 unmatched census."""
import argparse
import json
from pathlib import Path


def verify(baseline, classified):
    rows = classified["classification"]
    valid_sides = {"only_in_earlier_year", "only_in_later_year"}
    valid_contexts = {"plant_present_other_year", "plant_absent_other_year"}
    keys = set()
    for row in rows:
        key = (row["year_a"], row["year_b"], row["side"], row["plant_context"])
        if key in keys or row["side"] not in valid_sides or row["plant_context"] not in valid_contexts:
            raise ValueError("Duplicate or invalid classification category")
        keys.add(key)
        if type(row["records"]) is not int or row["records"] < 0:
            raise ValueError("Invalid classification count")
    expected_keys = set()
    for pair in baseline["adjacent_year_pairs"]:
        a, b = pair["year_a"], pair["year_b"]
        for side, field in [("only_in_earlier_year", "not_matched_from_a"),
                            ("only_in_later_year", "not_matched_from_b")]:
            expected_keys.update((a,b,side,ctx) for ctx in valid_contexts)
            observed = sum(row["records"] for row in rows if
                           row["year_a"] == a and row["year_b"] == b and row["side"] == side)
            if observed != pair[field]:
                raise ValueError(f"Classification total mismatch for {a}->{b} {side}: {observed} != {pair[field]}")
    if keys != expected_keys:
        raise ValueError("Missing or unexpected classification categories")
    if baseline["source_url"] != classified["source_url"]:
        raise ValueError("Source provenance mismatch")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads((args.output_dir / "national_exact_key_baseline.json").read_text())
    classified = json.loads((args.output_dir / "unmatched_plant_context.json").read_text())
    verify(baseline, classified)
    print("E1.2 categories reconcile exactly with E1.1 national unmatched totals")


if __name__ == "__main__":
    main()
