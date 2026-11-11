"""Inspect EIA-860 original Plant/Generator workbook sheet and header schemas.

This diagnostic does not validate the fleet, BA mapping, or empirical dispatch.
"""
import argparse
import io
import json
import re
import zipfile
from pathlib import Path
from openpyxl import load_workbook

def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()

def locate_header(ws, kind):
    required = ("plant code", "generator id") if kind == "generator" else ("plant code",)
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 20), values_only=True):
        labels = [normalize(v) for v in row]
        if all(any(term in label for label in labels) for term in required):
            return labels
    return None

def inspect_archive(path):
    result = {"archive": Path(path).name, "workbooks": [], "candidates": []}
    with zipfile.ZipFile(path) as outer:
        for item in outer.infolist():
            if not item.filename.lower().endswith(".xlsx"):
                continue
            kind = ("generator" if "generator" in item.filename.lower() else
                    "plant" if "plant" in item.filename.lower() else None)
            if kind is None:
                continue
            wb = load_workbook(io.BytesIO(outer.read(item)), read_only=True, data_only=True)
            try:
                record = {"file": item.filename, "kind": kind, "sheets": []}
                for ws in wb.worksheets:
                    labels = locate_header(ws, kind)
                    sheet = {"name": ws.title, "rows_including_headers": ws.max_row,
                             "header_detected": labels is not None}
                    if labels is not None:
                        sheet["matching_columns"] = [v for v in labels if any(
                            token in v for token in ("plant code", "generator id", "balancing authority",
                                                     "nameplate capacity", "operating status", "operating year"))]
                        result["candidates"].append({"file": item.filename, "sheet": ws.title,
                                                     "kind": kind, "columns": sheet["matching_columns"]})
                    record["sheets"].append(sheet)
                result["workbooks"].append(record)
            finally:
                wb.close()
    kinds = {x["kind"] for x in result["candidates"]}
    result["ready_for_manual_schema_review"] = kinds == {"plant", "generator"}
    result["fleet_validated"] = False
    result["ba_mapping_validated"] = False
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archives", nargs="+")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    report = [inspect_archive(path) for path in args.archives]
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps([{"archive": x["archive"], "candidate_sheets": len(x["candidates"]),
                       "ready_for_manual_schema_review": x["ready_for_manual_schema_review"]}
                      for x in report], indent=2))
    if not all(x["ready_for_manual_schema_review"] for x in report):
        raise SystemExit("Plant/Generator column schema not identified; manual inspection required")
