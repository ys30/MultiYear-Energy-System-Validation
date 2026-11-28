"""Inspect 2025 EIA-860M snapshots for Mesa Wind generator IDs without inferring commissioning."""
import hashlib
import io
import json
import urllib.error
import urllib.request

from openpyxl import load_workbook

from audit_official_eia860_generator_keys import find_columns, normalized_header

MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")
GENERATOR_IDS = {"WGNS", "MWD1"}
FIELDS = ("status", "nameplate", "operatingyear", "operatingmonth", "retirementyear", "retirementmonth")


def parse_generator_workbook(raw):
    book = load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    hits = []
    recognized = []
    try:
        for sheet in book.worksheets:
            preview = list(sheet.iter_rows(min_row=1, max_row=30, values_only=True))
            try:
                header, plant_idx, gen_idx = find_columns(preview)
            except ValueError:
                continue
            recognized.append(sheet.title)
            headers = preview[header - 1]
            for rownum, row in enumerate(sheet.iter_rows(min_row=header + 1, values_only=True), header + 1):
                try:
                    plant = int(row[plant_idx])
                except (TypeError, ValueError, IndexError):
                    continue
                if plant != 50535 or gen_idx >= len(row):
                    continue
                gen = str(row[gen_idx] or "").strip()
                if gen not in GENERATOR_IDS:
                    continue
                fields = {}
                for i, name in enumerate(headers):
                    norm = normalized_header(name)
                    if norm and any(token in norm for token in FIELDS):
                        fields[str(name)] = str(row[i]).strip() if i < len(row) and row[i] is not None else None
                hits.append({"generator_id": gen, "sheet": sheet.title, "row": rownum, "fields": fields})
    finally:
        book.close()
    if not recognized:
        raise ValueError("No EIA generator sheets recognized")
    return recognized, hits


def main():
    checked = 0
    for month in MONTHS:
        url = f"https://www.eia.gov/electricity/data/eia860m/archive/xls/{month}_generator2025.xlsx"
        req = urllib.request.Request(url, headers={"User-Agent": "ProjectA-Research/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                raw = response.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            print("EIA860M_MESA_2025_SOURCE_UNAVAILABLE=" + json.dumps({
                "month": month, "url": url, "error_type": type(exc).__name__,
                "physical_commissioning_verified": False}), flush=True)
            continue
        if not raw.startswith(b"PK"):
            raise ValueError(f"Unexpected XLSX signature for {month} 2025")
        sheets, hits = parse_generator_workbook(raw)
        if len({r["generator_id"] for r in hits}) != len(hits):
            raise AssertionError(f"Duplicate Mesa generator ID in {month} 2025")
        checked += 1
        print("EIA860M_MESA_2025_SNAPSHOT=" + json.dumps({
            "month": month, "year": 2025, "url": url, "sha256": hashlib.sha256(raw).hexdigest(),
            "recognized_sheets": sheets, "records": hits,
            "missing_id_does_not_prove_physical_absence": True,
            "generator_identity_crosswalk_verified": False,
            "empirical_dispatch_approved": False,
        }, sort_keys=True), flush=True)
    if checked != len(MONTHS):
        raise AssertionError(f"Incomplete 2025 Mesa monthly source coverage: {checked}/{len(MONTHS)}")
    print("EIA860M_MESA_2025_PROBE_SUMMARY=" + json.dumps({
        "requested_months": len(MONTHS), "downloaded_months": checked,
        "physical_commissioning_verified": False, "empirical_dispatch_approved": False,
    }), flush=True)


if __name__ == "__main__":
    main()
