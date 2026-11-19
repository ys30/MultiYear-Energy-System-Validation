"""Inspect official EIA-860M December snapshots for WGNS; no physical-event inference."""
import hashlib
import io
import json
import urllib.request

from openpyxl import load_workbook

from audit_official_eia860_generator_keys import find_columns, normalized_header


def main():
    results = []
    for year, month in ((2023, "december"),) + tuple((2024, m) for m in ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")):
        url = f"https://www.eia.gov/electricity/data/eia860m/archive/xls/{month}_generator{year}.xlsx"
        req = urllib.request.Request(url, headers={"User-Agent": "ProjectA-Research/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                raw = response.read()
        except Exception as exc:
            if (year, month) in ((2023, "december"), (2024, "march"), (2024, "june"), (2024, "september"), (2024, "december")):
                raise
            print("EIA860M_QUARTERLY_SOURCE_UNAVAILABLE=" + json.dumps({"year": year, "month": month, "url": url, "error_type": type(exc).__name__}), flush=True)
            continue
        if not raw.startswith(b"PK"):
            raise ValueError(f"{year}: not a valid XLSX ZIP signature")
        book = load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
        hits = []
        sheets = []
        for sheet in book.worksheets:
            preview = list(sheet.iter_rows(min_row=1, max_row=30, values_only=True))
            try:
                header, plant_idx, generator_idx = find_columns(preview)
            except ValueError:
                continue
            sheets.append(sheet.title)
            headers = preview[header - 1]
            for rownum, row in enumerate(sheet.iter_rows(min_row=header+1, values_only=True), header+1):
                try:
                    plant = int(row[plant_idx])
                except (ValueError, TypeError, IndexError):
                    continue
                if plant != 50535 or str(row[generator_idx] or "").strip() != "WGNS":
                    continue
                fields = {}
                for i, name in enumerate(headers):
                    norm = normalized_header(name)
                    if norm and any(term in norm for term in ("status", "nameplate", "operatingyear", "operatingmonth", "retirementyear", "retirementmonth")):
                        fields[str(name)] = str(row[i]).strip() if i < len(row) and row[i] is not None else None
                hits.append({"sheet": sheet.title, "row": rownum, "fields": fields})
        book.close()
        if not sheets:
            raise ValueError(f"{year}: no generator sheets recognized")
        result = {"year": year, "month": month, "source_url": url, "sha256": hashlib.sha256(raw).hexdigest(),
                  "recognized_sheets": sheets, "WGNS_50535_records": hits}
        results.append(result)
        print("EIA860M_WGNS_SNAPSHOT=" + json.dumps(result, sort_keys=True), flush=True)
    print("EIA860M_WGNS_COMPARISON=" + json.dumps({
        "snapshots_checked": len(results), "requested_snapshots": 13, "physical_restart_verified": False,
        "generator_identity_crosswalk_verified": False, "empirical_dispatch_approved": False}))


if __name__ == "__main__":
    main()
