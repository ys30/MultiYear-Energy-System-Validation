"""Exact-key annual EIA-860 workbook audit; never infer physical absence."""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from openpyxl import load_workbook


def normalized_header(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def find_columns(rows):
    for rownum, values in enumerate(rows[:30], 1):
        norm = [normalized_header(x) for x in values]
        plant = next((i for i, s in enumerate(norm) if s in ("plantcode", "plantid", "plantideia")), None)
        gen = next((i for i, s in enumerate(norm) if s in ("generatorid", "generator")), None)
        if plant is not None and gen is not None:
            return rownum, plant, gen
    raise ValueError("Could not independently identify Plant Code and Generator ID columns")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive-dir", required=True)
    p.add_argument("--targets", default="data/pudl/project_a_pudl_29_targets.csv")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    with open(args.targets, newline="", encoding="utf-8-sig") as f:
        targets = [(int(r["plant_id_eia"]), r["generator_id"].strip())
                   for r in csv.DictReader(f)]
    if len(targets) != 29 or len(set(targets)) != 29:
        raise ValueError("Expected 29 distinct target keys")
    receipts = []
    matrix = []
    for year in (2023, 2024, 2025):
        archive = Path(args.archive_dir) / f"eia860{year}.zip"
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if not zipfile.is_zipfile(archive):
            raise ValueError(f"{year}: invalid ZIP")
        with zipfile.ZipFile(archive) as z:
            members = [name for name in z.namelist() if
                       re.search(r"3_1_Generator_Y" + str(year) + r"\.xlsx$", name, re.I)]
            if len(members) != 1:
                raise ValueError(f"{year}: expected one annual generator workbook, got {members}")
            workbook = load_workbook(io.BytesIO(z.read(members[0])), read_only=True, data_only=True)
            exact = {}
            sheets = []
            recognized_sheets = 0
            target_rows = {}
            target_metadata = {}
            for sheet in workbook.worksheets:
                preview = list(sheet.iter_rows(min_row=1, max_row=30, values_only=True))
                try:
                    header_row, plant_idx, gen_idx = find_columns(preview)
                except ValueError:
                    sheets.append({"sheet": sheet.title, "status": "unrecognized_header"})
                    continue
                recognized_sheets += 1
                count = 0
                for rownum, row in enumerate(sheet.iter_rows(min_row=header_row + 1, values_only=True), header_row + 1):
                    if len(row) <= max(plant_idx, gen_idx):
                        continue
                    try:
                        plant = int(row[plant_idx])
                    except (TypeError, ValueError):
                        continue
                    generator = str(row[gen_idx] or "").strip()
                    if not generator:
                        continue
                    key = (plant, generator)
                    if key in targets:
                        record = {"sheet": sheet.title, "row": rownum}
                        exact.setdefault(key, []).append(record)
                        header_values = preview[header_row - 1]
                        selected = {}
                        for idx, label in enumerate(header_values):
                            name = normalized_header(label)
                            if name and any(token in name for token in ("status", "nameplate", "operatingyear", "operationyear", "operatingmonth", "operationmonth")):
                                selected[str(label)] = str(row[idx]) if idx < len(row) and row[idx] is not None else None
                        target_metadata.setdefault(key, []).append({"sheet": sheet.title, "row": rownum, "fields": selected})
                        target_rows.setdefault(key, []).append({"sheet": sheet.title, "row": rownum,
                            "raw_values": [str(value)[:120] if value is not None else None for value in row[:35]],
                            "column_headers": [str(value)[:100] if value is not None else None for value in preview[header_row - 1][:35]]})
                    count += 1
                sheets.append({"sheet": sheet.title, "rows_with_keys": count,
                               "header_row": header_row})
            workbook.close()
            if recognized_sheets == 0:
                raise ValueError(f"{year}: no recognized generator data sheets")
        for plant, generator in targets:
            matches = exact.get((plant, generator), [])
            matrix.append({"year": year, "plant_id_eia": plant, "generator_id": generator,
                           "exact_official_records": matches,
                           "official_record_fields": target_rows.get((plant, generator), []),
                           "official_selected_metadata": target_metadata.get((plant, generator), []),
                           "exact_match": bool(matches),
                           "physical_absence_inferred": False,
                           "commissioning_verified": False})
        receipts.append({"year": year, "zip_sha256": digest, "member": members[0],
                         "recognized_generator_sheets": recognized_sheets,
                         "targets_with_multiple_official_rows": sum(len(v) > 1 for v in exact.values()),
                         "sheets": sheets, "target_exact_matches": sum(
                             bool(exact.get(k)) for k in targets)})
        print(f"{year}: {receipts[-1]['target_exact_matches']}/29 exact official annual matches", flush=True)
    if len(matrix) != 87:
        raise RuntimeError("Incomplete official annual evidence matrix")
    output = {"schema_version": 1, "source_kind": "official_EIA860_annual_workbooks",
              "annual_sources": receipts, "target_year_records": matrix,
              "physical_commissioning_verified": False,
              "empirical_dispatch_approved": False}
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
