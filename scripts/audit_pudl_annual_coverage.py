"""Audit annual PUDL source coverage without interpreting absent rows as absent assets.

Input: exported annual generator CSV with plant_id_eia,generator_id,report_date.
Output: descriptive coverage receipt. This is NOT a commissioning or dispatch gate.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def audit(source, targets, years=(2023, 2024, 2025)):
    with open(targets, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"plant_id_eia", "generator_id"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Target CSV missing plant_id_eia or generator_id")
        target_rows = list(reader)
    keys = [(int(r["plant_id_eia"]), r["generator_id"].strip()) for r in target_rows]
    if not keys or len(set(keys)) != len(keys) or any(not g for _, g in keys):
        raise ValueError("Empty, duplicate, or invalid target keys")

    annual = defaultdict(set)
    plants = defaultdict(set)
    counts = Counter()
    with open(source, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"plant_id_eia", "generator_id", "report_date"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Source CSV missing required columns")
        for i, row in enumerate(reader, start=2):
            try:
                year = date.fromisoformat(row["report_date"][:10]).year
                plant = int(row["plant_id_eia"])
                generator = row["generator_id"].strip()
                if not generator:
                    raise ValueError("blank generator")
            except (TypeError, ValueError, AttributeError) as exc:
                raise ValueError(f"Invalid source row {i}") from exc
            counts[year] += 1
            key = (plant, generator)
            if key in annual[year]:
                raise ValueError(f"Duplicate annual generator key {year}: {key}")
            annual[year].add(key)
            plants[year].add(plant)

    missing = set(years) - set(counts)
    if missing:
        raise ValueError(f"Entire requested years missing from source: {sorted(missing)}")

    rows = []
    for (plant, generator), target in zip(keys, target_rows):
        for year in years:
            exact = (plant, generator) in annual[year]
            plant_found = plant in plants[year]
            rows.append({
                "plant_id_eia": plant,
                "generator_id": generator,
                "year": year,
                "exact_generator_record": exact,
                "plant_has_other_or_same_generator_record": plant_found,
                "classification": "exact_match" if exact else
                    ("plant_present_generator_unmatched" if plant_found else "plant_unmatched"),
                "physical_absence_inferred": False,
                "commissioning_verified": False,
            })

    return {
        "schema_version": 1,
        "input_kind": "PUDL_annual_generators",
        "source_sha256": sha256(source),
        "targets_sha256": sha256(targets),
        "source_rows_by_year": {str(y): counts[y] for y in years},
        "unique_generators_by_year": {str(y): len(annual[y]) for y in years},
        "unique_plants_by_year": {str(y): len(plants[y]) for y in years},
        "target_exact_matches_by_year": {
            str(y): sum(r["year"] == y and r["exact_generator_record"] for r in rows)
            for y in years
        },
        "target_plant_matches_by_year": {
            str(y): sum(r["year"] == y and r["plant_has_other_or_same_generator_record"] for r in rows)
            for y in years
        },
        "records": rows,
        "coverage_complete_for_target_cohort": None,
        "physical_commissioning_verified": False,
        "empirical_dispatch_approved": False,
        "interpretation": "Unmatched means no matching record in this export; it does not establish physical absence.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--annual-csv", required=True)
    p.add_argument("--targets", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--sha256", required=True, help="Pinned SHA256 of annual source")
    p.add_argument("--release", required=True, help="Immutable PUDL release identifier")
    a = p.parse_args()
    if not a.release.strip() or a.release.lower() in ("latest", "nightly") or a.release.startswith("fixture-"):
        p.error("An immutable non-fixture release identifier is required")
    if len(a.sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in a.sha256):
        p.error("A valid pinned SHA256 is required")
    if sha256(a.annual_csv).lower() != a.sha256.lower():
        p.error("Source checksum mismatch")
    result = audit(a.annual_csv, a.targets)
    result["release"] = a.release
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
