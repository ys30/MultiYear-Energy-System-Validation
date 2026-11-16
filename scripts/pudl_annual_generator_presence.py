"""Build a fail-closed PUDL annual generator presence matrix for the fixed 29-key cohort.

This tool consumes an already exported annual generator CSV, NOT an EIA-860M
changelog. Absence of a row is reporting absence, not physical absence.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

from pudl_pre2025_entrant_crosscheck import read_targets

YEARS = (2023, 2024, 2025)

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def run(targets, source, output, release, expected_sha256):
    if not release or release.lower() in ("latest", "nightly") or release.startswith("fixture-"):
        raise ValueError("Real annual matrix requires immutable non-fixture release")
    if not expected_sha256 or len(expected_sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in expected_sha256):
        raise ValueError("Pinned 64-character SHA256 is mandatory")
    actual = digest(source)
    if actual.lower() != expected_sha256.lower():
        raise ValueError("Annual PUDL input SHA256 mismatch")
    _, keys = read_targets(targets)
    target_set = set(keys)
    seen = set()
    present = set()
    source_rows = 0
    source_years = Counter()
    with open(source, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not {"plant_id_eia", "generator_id", "report_date"}.issubset(reader.fieldnames):
            raise ValueError("Annual PUDL CSV must include plant_id_eia,generator_id,report_date")
        for row in reader:
            source_rows += 1
            try:
                plant = int(row["plant_id_eia"])
                generator = row["generator_id"].strip()
                d = date.fromisoformat(row["report_date"][:10])
            except (ValueError, TypeError, AttributeError) as exc:
                raise ValueError(f"Invalid annual row {source_rows}") from exc
            if not generator:
                raise ValueError("Blank generator_id")
            source_years[d.year] += 1
            key = (plant, generator, d.year)
            if key in seen:
                raise ValueError(f"Duplicate plant/generator/year key: {key}")
            seen.add(key)
            if (plant, generator) in target_set and d.year in YEARS:
                present.add(key)
    if not source_rows:
        raise ValueError("Empty annual source")
    missing_years = set(YEARS) - set(source_years)
    if missing_years:
        raise ValueError(f"Annual source missing entire requested report years: {sorted(missing_years)}")
    records = [
        {"plant_id_eia": plant, "generator_id": generator,
         "presence": {str(y): (plant, generator, y) in present for y in YEARS}}
        for plant, generator in keys
    ]
    summary = {str(y): sum((plant, generator, y) in present for plant, generator in keys) for y in YEARS}
    result = {
        "release": release, "source_sha256": actual, "targets_sha256": digest(targets),
        "input_kind": "PUDL_annual_generators_not_changelog",
        "source_rows": source_rows, "source_rows_by_year": {str(y): source_years[y] for y in YEARS}, "targets": len(keys),
        "present_by_year": summary, "missing_by_year": {str(y): len(keys) - summary[str(y)] for y in YEARS},
        "records": records, "physical_commissioning_verified": False,
        "pudl_annual_presence_audited": True, "pudl_changelog_matched": False,
        "empirical_dispatch_approved": False,
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True)
    parser.add_argument("--annual-csv", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run(args.targets, args.annual_csv, args.output, args.release, args.sha256)
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))
