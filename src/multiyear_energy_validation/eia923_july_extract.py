"""Extract July 2025 EIA-923 observations for the commissioning-screened sites.

Page 1 is plant/prime-mover/fuel aggregated; Page 4 is generator-level
where reported. Do not sum the two or treat net generation as availability.
"""
import csv
import json
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from .eia923_official_source import URL


def _normalize(value):
    return " ".join(str(value or "").lower().split())


def _find_column(headers, *terms):
    candidates = [i for i, h in enumerate(headers)
                  if all(term in _normalize(h) for term in terms)]
    if len(candidates) != 1:
        raise ValueError(f"expected unique column for {terms}, found {candidates}")
    return candidates[0]


def _number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
        import math
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def extract_july(archive_path, cohort_path, output_path):
    cohort = json.loads(Path(cohort_path).read_text(encoding="utf-8"))
    eligible = {str(x["plant_id"]) for x in cohort["chronology_screened_sites"]}
    rows_out = []
    sheet_counts = defaultdict(int)
    with ZipFile(archive_path) as archive:
        workbooks = [n for n in archive.namelist() if n.lower().endswith(".xlsx") and "Schedules_2_3_4_5" in n]
        if len(workbooks) != 1:
            raise ValueError(f"expected exactly one schedules workbook: {workbooks}")
        with archive.open(workbooks[0]) as f:
            book = load_workbook(BytesIO(f.read()), read_only=True, data_only=True)
        try:
            for sheet_name in ("Page 1 Generation and Fuel Data", "Page 1 Energy Storage", "Page 4 Generator Data"):
                ws = book[sheet_name]
                it = ws.iter_rows(values_only=True)
                for _ in range(5):
                    next(it)
                headers = next(it)
                plant_idx = _find_column(headers, "plant id")
                # EIA-923 has grouped two-level headers: row 5 is the measure
                # group, row 6 is the month label. Resolve the month within
                # the rightmost preceding Net Generation group.
                groups = list(ws.iter_rows(min_row=5, max_row=5, values_only=True))[0]
                netgen_starts = [i for i, value in enumerate(groups)
                                 if "net generation" in _normalize(value)]
                if not netgen_starts:
                    raise ValueError(f"missing net generation group in {sheet_name}: {groups}")
                start = netgen_starts[-1]
                july_candidates = [i for i in range(start, len(headers))
                                   if "july" in _normalize(headers[i])]
                if len(july_candidates) != 1:
                    raise ValueError(f"ambiguous July column in {sheet_name}: "
                                     f"start={start}, candidates={july_candidates}, "
                                     f"headers={headers}")
                july_idx = july_candidates[0]
                name_idx = _find_column(headers, "plant name")
                fuel_idx = (_find_column(headers, "reported", "fuel type code")
                            if sheet_name != "Page 4 Generator Data" else None)
                gen_idx = (_find_column(headers, "generator id")
                           if sheet_name == "Page 4 Generator Data" else None)
                for row_num, values in enumerate(it, 7):
                    plant_raw = values[plant_idx]
                    try:
                        plant = str(int(plant_raw))
                    except (TypeError, ValueError):
                        continue
                    if plant not in eligible:
                        continue
                    generation = _number(values[july_idx])
                    rows_out.append({
                        "plant_id":plant, "plant_name":str(values[name_idx] or ""),
                        "source_sheet":sheet_name,"source_row":row_num,
                        "generator_id":str(values[gen_idx] or "") if gen_idx is not None else "",
                        "fuel_code":str(values[fuel_idx] or "") if fuel_idx is not None else "",
                        "net_generation_july_mwh":generation,
                        "generation_value_status":"numeric" if generation is not None else "not_numeric_or_missing",
                    })
                    sheet_counts[sheet_name] += 1
        finally:
            book.close()
    output = {
        "source_url":URL, "source_workbook":workbooks[0],
        "year":2025,"month":7,"commissioning_screened_plant_ids":sorted(eligible),
        "rows":rows_out,"matched_rows_by_sheet":dict(sheet_counts),
        "plant_monthly_generation_is_not_hourly_availability":True,
        "page1_and_page4_must_not_be_summed":True,
        "storage_separate_from_generation":True,
        "independent_generation_attribution_reviewed":False,
        "empirical_dispatch_approved":False,
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_JULY2025_EXTRACT="+json.dumps({
        "source_workbook":workbooks[0],
        "matched_rows_by_sheet":dict(sheet_counts),
        "plants":[{"plant_id":pid,"observations":[
            {"source_sheet":r["source_sheet"],"source_row":r["source_row"],
             "generator_id":r["generator_id"],"fuel_code":r["fuel_code"],
             "net_generation_july_mwh":r["net_generation_july_mwh"]}
            for r in rows_out if r["plant_id"]==pid]} for pid in sorted(eligible)],
        "attribution_reviewed":False,"empirical_dispatch_approved":False,
    },sort_keys=True))
    return output


def main():
    extract_july("outputs/eia923/2025/f923_2025.zip",
                 "outputs/spatial_weather_merged_2025/july2025_commissioning_screened_cohort.json",
                 "outputs/spatial_weather_merged_2025/eia923_july2025_five_site_extract.json")


if __name__ == "__main__":
    main()
