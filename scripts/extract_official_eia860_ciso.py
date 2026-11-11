"""Produce auditable CISO generator-row extracts from original EIA-860 workbooks.

Fail closed when the original schema is ambiguous. This is a staging extract,
not independent certification of the 2024–2025 fleet bridge.
"""
import argparse
import csv
import io
import json
import re
import zipfile
from pathlib import Path
from openpyxl import load_workbook

def norm(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()

def find_header(sheet, required):
    for n, row in enumerate(sheet.iter_rows(min_row=1, max_row=40, values_only=True), 1):
        labels = [norm(v) for v in row]
        if all(any(x in v for v in labels) for x in required):
            return n, labels
    raise ValueError(f"No header with {required}: {sheet.title}")

def pick(labels, candidates):
    hits = [i for i, label in enumerate(labels) if label in candidates]
    if len(hits) != 1:
        raise ValueError(f"Ambiguous column {candidates}: {[(i,labels[i]) for i in hits]}")
    return hits[0]

def extract(archive_path, year, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        files = archive.namelist()
        plant_files = [x for x in files if re.search(r"(^|/)2___Plant_", x, re.I) and x.endswith(".xlsx")]
        gen_files = [x for x in files if re.search(r"(^|/)3_1_Generator_", x, re.I) and x.endswith(".xlsx")]
        if len(plant_files) != 1 or len(gen_files) != 1:
            raise ValueError(f"Expected one Plant and one Generator workbook: {plant_files}, {gen_files}")
        plant = load_workbook(io.BytesIO(archive.read(plant_files[0])), read_only=True, data_only=True)
        gen = load_workbook(io.BytesIO(archive.read(gen_files[0])), read_only=True, data_only=True)
        try:
            ba_by_plant = {}
            for sheet in plant.worksheets:
                try:
                    n, labels = find_header(sheet, ("plant code",))
                    pid = pick(labels, {"plant code"})
                    ba = pick(labels, {"balancing authority code", "balancing authority"})
                except ValueError:
                    continue
                for row in sheet.iter_rows(min_row=n+1, values_only=True):
                    if len(row) <= max(pid, ba) or row[pid] is None:
                        continue
                    plant_id = str(row[pid]).strip().removesuffix(".0")
                    authority = str(row[ba] or "").strip()
                    if plant_id in ba_by_plant and ba_by_plant[plant_id] != authority:
                        raise ValueError(f"Conflicting BA for plant {plant_id}")
                    ba_by_plant[plant_id] = authority
            if not ba_by_plant:
                raise ValueError("No Plant-to-BA rows extracted")
            records = {}
            schema = []
            for sheet in gen.worksheets:
                try:
                    n, labels = find_header(sheet, ("plant code", "generator id"))
                    pid = pick(labels, {"plant code"})
                    gid = pick(labels, {"generator id"})
                    status = pick(labels, {"status", "operational status", "operating status"})
                    capacity = pick(labels, {"nameplate capacity mw", "nameplate capacity"})
                except ValueError:
                    continue
                schema.append({"sheet":sheet.title, "header_row":n,
                               "plant_code_col":pid, "generator_id_col":gid,
                               "status_col":status, "nameplate_col":capacity})
                for row in sheet.iter_rows(min_row=n+1, values_only=True):
                    if len(row) <= max(pid,gid,status,capacity) or row[pid] is None or row[gid] is None:
                        continue
                    plant_id = str(row[pid]).strip().removesuffix(".0")
                    if ba_by_plant.get(plant_id) != "CISO":
                        continue
                    key = (plant_id, str(row[gid]).strip())
                    if key in records:
                        raise ValueError(f"Duplicate CISO generator key: {key}")
                    records[key] = {"year":year, "plant_id_eia":plant_id, "generator_id":key[1],
                                    "status":str(row[status] or "").strip(),
                                    "nameplate_mw":row[capacity],
                                    "plant_ba":"CISO", "source_sheet":sheet.title}
            if not schema or not records:
                raise ValueError("No usable Generator schema or CISO rows")
            csv_path = out_dir / f"eia860_ciso_generators_{year}.csv"
            with csv_path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(next(iter(records.values())).keys()))
                writer.writeheader()
                writer.writerows(records.values())
            report = {"year":year, "plant_ba_rows":len(ba_by_plant),
                      "ciso_generator_rows":len(records), "generator_schemas":schema,
                      "scope":"unvalidated_staging_extract", "fleet_validated":False,
                      "ba_mapping_validated":False}
            (out_dir / f"eia860_ciso_extract_{year}.json").write_text(json.dumps(report,indent=2)+"\n")
            return report
        finally:
            plant.close()
            gen.close()

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",required=True)
    parser.add_argument("--year",type=int,required=True)
    parser.add_argument("--out-dir",required=True)
    args=parser.parse_args()
    print(json.dumps(extract(args.archive,args.year,args.out_dir),indent=2))
