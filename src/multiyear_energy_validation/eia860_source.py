"""Download and audit official annual EIA-860 archives without mapping assumptions."""
import argparse
import hashlib
import json
import io
import urllib.request
import zipfile
from pathlib import Path

URLS = {
    2024: "https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip",
    2025: "https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip",
}


def intake(year, output):
    if year not in URLS:
        raise ValueError("Only verified official 2024/2025 EIA-860 URLs are supported")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    url = URLS[year]
    request = urllib.request.Request(url, headers={"User-Agent": "MultiYear-Energy-Validation/0.1 (research)"})
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    if not zipfile.is_zipfile(__import__("io").BytesIO(data)):
        raise ValueError("Official response is not a ZIP archive")
    archive = output / f"eia860{year}.zip"
    archive.write_bytes(data)
    with zipfile.ZipFile(archive) as zf:
        entries = [
            {"name": info.filename, "bytes": info.file_size}
            for info in zf.infolist() if not info.is_dir()
        ]
    # Read only the top few rows of plant/generator workbooks. Never guess
    # which row is the header or which field represents balancing authority.
    from openpyxl import load_workbook
    layouts = {}
    with zipfile.ZipFile(archive) as zf:
        for member in zf.namelist():
            if not (member.endswith(".xlsx") and (
                "Plant_Y" in member or "Generator_Y" in member or "LayoutY" in member
            )):
                continue
            wb = load_workbook(io.BytesIO(zf.read(member)), read_only=True, data_only=True)
            sheets = {}
            for ws in wb.worksheets:
                preview = []
                for row in ws.iter_rows(max_row=8, max_col=45, values_only=True):
                    preview.append([str(v)[:160] if v is not None else None for v in row])
                sheets[ws.title] = {"preview_first_8_rows_first_45_columns": preview}
            layouts[member] = sheets
            wb.close()
    (output / "workbook_layouts.json").write_text(json.dumps(layouts, indent=2))
    for book, sheets in layouts.items():
        for sheet, audit in sheets.items():
            print("EIA860_SHEET_PREVIEW=" + json.dumps({"year": year, "workbook": book, "sheet": sheet, **audit}, sort_keys=True))
    inventory = {
        "year": year, "source_url": url, "sha256": hashlib.sha256(data).hexdigest(),
        "archive_bytes": len(data), "entries": entries,
        "workbook_layouts_recorded": sorted(layouts),
        "generation_fleet_validated": False,
        "balancing_authority_mapping_validated": False,
        "dispatch_model_approved": False,
    }
    (output / "source_inventory.json").write_text(json.dumps(inventory, indent=2))
    print("EIA860_SOURCE_INVENTORY=" + json.dumps(inventory, sort_keys=True))
    return inventory


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True, choices=sorted(URLS))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    intake(args.year, args.output)
