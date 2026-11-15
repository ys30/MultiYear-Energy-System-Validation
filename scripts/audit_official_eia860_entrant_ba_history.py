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


def earlier_year_presence(archives_by_year, plant_ids):
    """Report annual Plant-sheet presence; missing annual records are not proof of absence."""
    history = {}
    for year, archive in sorted(archives_by_year.items()):
        if year >= 2024:
            raise ValueError("Earlier-year archives must precede 2024")
        reported = plant_ba(archive)
        history[str(year)] = {
            plant: {"in_plant_sheet": plant in reported,
                    "reported_ba": reported.get(plant, "")}
            for plant in sorted(plant_ids)
        }
    return history


def audit(archive_2024, archive_2025, targets=TARGETS, earlier_archives=None):
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
    historical = earlier_year_presence(earlier_archives or {}, {r["plant_id_eia"] for r in evidence})
    categories = sorted({r["classification"] for r in evidence})
    plants = {}
    for row in evidence:
        plant = row["plant_id_eia"]
        classification = row["classification"]
        if plant in plants and plants[plant] != classification:
            raise ValueError(f"Conflicting BA history classification within plant {plant}")
        plants[plant] = classification
    plant_counts = {c: sum(value == c for value in plants.values()) for c in categories}
    assert sum(plant_counts.values()) == len(plants)
    return {"scope": "year_specific_original_plant_sheet_reported_ba_only",
            "record_count": len(evidence),
            "unique_plant_count": len({r["plant_id_eia"] for r in evidence}),
            "classification_counts": {c: sum(r["classification"] == c for r in evidence)
                                      for c in categories},
            "unique_plant_classification_counts": plant_counts,
            "earlier_plant_sheet_history": historical,
            "earlier_history_years_checked": sorted(historical),
            "historical_ba_reporting_audited": True,
            "physical_ba_transfer_verified": False,
            "pudl_matched": False, "ba_mapping_validated": False,
            "empirical_dispatch_approved": False, "evidence_rows": evidence}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-2024", required=True)
    parser.add_argument("--archive-2025", required=True)
    parser.add_argument("--targets", default=str(TARGETS))
    parser.add_argument("--earlier-archive", action="append", default=[],
                        help="YEAR=PATH for a pinned earlier EIA-860 ZIP; repeatable")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    earlier = {}
    for item in args.earlier_archive:
        year, separator, path = item.partition("=")
        if not separator or not year.isdigit() or not path or int(year) in earlier:
            parser.error("--earlier-archive must be unique YEAR=PATH")
        earlier[int(year)] = path
    result = audit(args.archive_2024, args.archive_2025, args.targets, earlier)
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
