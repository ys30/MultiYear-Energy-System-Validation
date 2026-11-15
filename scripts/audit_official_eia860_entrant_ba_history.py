"""Audit 2024/2025 original EIA-860 Plant-sheet BA assignments for 29 entrant plants.

A Plant-sheet BA code is annual reported metadata, not proof of physical transfer.
"""
import argparse
import csv
import io
import json
import re
import zipfile
from pathlib import Path

from openpyxl import load_workbook
from extract_official_eia860_ciso import find_header, pick

TARGETS = Path(__file__).resolve().parents[1] / "data/pudl/project_a_pudl_29_targets.csv"


def plant_ba(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        matches = [name for name in archive.namelist()
                   if re.search(r"(^|/)2___Plant_", name, re.I) and name.endswith(".xlsx")]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one Plant workbook: {matches}")
        wb = load_workbook(io.BytesIO(archive.read(matches[0])), read_only=True, data_only=True)
        try:
            found = {}
            matched_sheets = 0
            for sheet in wb.worksheets:
                try:
                    n, labels = find_header(sheet, ("plant code",))
                    pid = pick(labels, {"plant code"})
                    ba = pick(labels, {"balancing authority code", "balancing authority"})
                except ValueError:
                    continue
                matched_sheets += 1
                for row in sheet.iter_rows(min_row=n + 1, values_only=True):
                    if len(row) <= max(pid, ba) or row[pid] is None:
                        continue
                    key = str(row[pid]).strip().removesuffix(".0")
                    value = str(row[ba] or "").strip().upper()
                    if key in found and found[key] != value:
                        raise ValueError(f"Conflicting BA for plant {key}")
                    found[key] = value
            if not matched_sheets:
                raise ValueError("No Plant worksheet with BA column")
            return found
        finally:
            wb.close()


def audit(archive_2024, archive_2025, targets=TARGETS):
    with open(targets, newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 29:
        raise ValueError(f"Expected 29 targets, got {len(rows)}")
    before = plant_ba(archive_2024)
    after = plant_ba(archive_2025)
    evidence = []
    for row in rows:
        plant = row["plant_id_eia"].strip()
        ba24, ba25 = before.get(plant), after.get(plant)
        if ba25 != "CISO":
            raise ValueError(f"2025 plant {plant} does not report CISO: {ba25}")
        if ba24 is None:
            classification = "not_in_2024_plant_sheet"
        elif not ba24:
            classification = "2024_ba_blank"
        elif ba24 != "CISO":
            classification = "reported_ba_changed_to_ciso"
        else:
            classification = "ciso_both_years_generator_absent_2024"
        evidence.append({"plant_id_eia": plant, "generator_id": row["generator_id"],
                         "reported_operating_year": row["reported_operating_year"],
                         "plant_ba_2024": ba24 or "", "plant_ba_2025": ba25,
                         "plant_in_2024_sheet": ba24 is not None,
                         "classification": classification})
    categories = sorted({r["classification"] for r in evidence})
    return {"scope": "year_specific_original_plant_sheet_reported_ba_only",
            "record_count": len(evidence),
            "unique_plant_count": len({r["plant_id_eia"] for r in evidence}),
            "classification_counts": {c: sum(r["classification"] == c for r in evidence)
                                      for c in categories},
            "historical_ba_reporting_audited": True,
            "physical_ba_transfer_verified": False,
            "pudl_matched": False, "ba_mapping_validated": False,
            "empirical_dispatch_approved": False, "evidence_rows": evidence}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-2024", required=True)
    parser.add_argument("--archive-2025", required=True)
    parser.add_argument("--targets", default=str(TARGETS))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = audit(args.archive_2024, args.archive_2025, args.targets)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    evidence_path = destination.with_name("independent-29-entrant-plant-ba-rows.csv")
    with evidence_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result["evidence_rows"][0]))
        writer.writeheader()
        writer.writerows(result["evidence_rows"])
    result["evidence_rows_artifact"] = evidence_path.name
    del result["evidence_rows"]
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(destination.read_text())
