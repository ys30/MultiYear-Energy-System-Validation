"""Reconcile E1.3 technology/MW group counts to E1.2 plant-context counts."""
import argparse
import json
from pathlib import Path


def verify(classification, capacity):
    if classification["source_url"] != capacity["source_url"]:
        raise ValueError("Source provenance mismatch")
    expected = {(r["year_a"],r["year_b"],r["side"],r["plant_context"]):r["records"]
                for r in classification["classification"]}
    actual = {}
    for row in capacity["rows"]:
        key = (row["year_a"],row["year_b"],row["side"],row["plant_context"])
        if key not in expected:
            raise ValueError(f"Unexpected E1.3 group: {key}")
        n=row["records"]
        if type(n) is not int or n<0:
            raise ValueError("Invalid E1.3 record count")
        if not 0<=row["records_with_capacity"]<=n:
            raise ValueError("Invalid nonnull capacity count")
        if not 0<=row["negative_capacity_records"]<=row["records_with_capacity"]:
            raise ValueError("Invalid negative capacity count")
        actual[key]=actual.get(key,0)+n
    if expected != actual:
        raise ValueError(f"E1.3 classification reconciliation mismatch: {expected} vs {actual}")
    return True


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    classification=json.loads((folder/"unmatched_plant_context.json").read_text())
    capacity=json.loads((folder/"unmatched_capacity_by_technology.json").read_text())
    verify(classification,capacity)
    print("E1.3 technology/MW groups reconcile exactly to E1.2 counts")


if __name__=="__main__":
    main()
