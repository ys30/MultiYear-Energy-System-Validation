"""Compare July 2025 net generation with other months in the same official EIA-923 workbook.

This is a descriptive within-year context audit. EIA-860 year-end nameplate
is not necessarily valid for all earlier months; monthly capacity factors are
therefore intentionally not computed here.
"""
import json
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from openpyxl import load_workbook

from .eia923_july_extract import _normalize, _find_column, _number
from .eia923_official_source import URL

MONTHS=("january","february","march","april","may","june","july",
        "august","september","october","november","december")
FUELS={"57373":"SUN","57695":"SUN","57484":"WND","57514":"WND","7526":"WND"}


def audit_annual_months(archive_path, output_path):
    with ZipFile(archive_path) as archive:
        matches=[n for n in archive.namelist() if n.lower().endswith(".xlsx") and "Schedules_2_3_4_5" in n]
        if len(matches)!=1: raise ValueError("ambiguous official schedules workbook")
        with archive.open(matches[0]) as f:
            book=load_workbook(BytesIO(f.read()),read_only=True,data_only=True)
        try:
            ws=book["Page 1 Generation and Fuel Data"]
            rows=ws.iter_rows(values_only=True)
            for _ in range(4): next(rows)
            groups=next(rows)
            headers=next(rows)
            start_indices=[i for i,v in enumerate(groups) if "net generation" in _normalize(v)]
            if len(start_indices)!=1: raise ValueError("unexpected net generation header groups")
            start=start_indices[0]
            plant_i=_find_column(headers,"plant id")
            fuel_i=_find_column(headers,"reported","fuel type code")
            month_cols={}
            for month in MONTHS:
                matches=[i for i in range(start,len(headers)) if _normalize(headers[i])==f"net generation {month}" or _normalize(headers[i])==month or _normalize(headers[i])==f"net generation\n{month}"]
                if len(matches)!=1:
                    # EIA header may have whitespace or units, but month must be unambiguous
                    matches=[i for i in range(start,len(headers)) if month in _normalize(headers[i])]
                if len(matches)!=1: raise ValueError(f"ambiguous {month} net generation column: {matches}")
                month_cols[month]=matches[0]
            found=defaultdict(list)
            for row_num,row in enumerate(rows,7):
                try: pid=str(int(row[plant_i]))
                except (ValueError,TypeError): continue
                if pid not in FUELS or str(row[fuel_i] or "").strip()!=FUELS[pid]: continue
                found[pid].append((row_num,row))
            report=[]
            for pid in sorted(FUELS):
                matched=found[pid]
                if len(matched)!=1: raise ValueError(f"ambiguous plant/fuel {pid}: {len(matched)} rows")
                row_num,row=matched[0]
                months={m:_number(row[i]) for m,i in month_cols.items()}
                july=months["july"]
                if july is None: raise ValueError(f"July generation missing for {pid}")
                nonnegative=[v for v in months.values() if v is not None and v>=0]
                report.append({"plant_id":pid,"fuel_code":FUELS[pid],
                               "eia923_page1_source_row":row_num,
                               "monthly_net_generation_mwh":months,
                               "july_net_generation_mwh":july,
                               "july_rank_among_reported_nonnegative_months":
                                  1+sum(v>july for v in nonnegative),
                               "reported_nonnegative_months":len(nonnegative),
                               "monthly_capacity_factors_not_calculated":True})
        finally: book.close()
    output={"source_url":URL,"source_workbook":matches[0] if False else "EIA923_Schedules_2_3_4_5_M_12_2025_Final.xlsx",
            "year":2025,"sites":report,
            "year_end_capacity_not_assumed_constant_across_months":True,
            "monthly_generation_is_not_hourly_availability":True,
            "empirical_dispatch_approved":False}
    out=Path(output_path);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_FIVE_SITE_MONTHLY_CONTEXT="+json.dumps({"sites":report,"empirical_dispatch_approved":False},sort_keys=True))
    return output


if __name__=="__main__":
    audit_annual_months("outputs/eia923/2025/f923_2025.zip",
                        "outputs/spatial_weather_merged_2025/eia923_five_site_monthly_context.json")
