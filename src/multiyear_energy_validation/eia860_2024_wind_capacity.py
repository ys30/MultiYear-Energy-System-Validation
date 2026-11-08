"""Audit 2024 EIA-860 operating wind capacity before year-over-year inference."""
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
from .eia860_fleet import _id,_records

IDS=("57484","57514","7526")

def audit(zip_path,output_path):
    groups=defaultdict(list)
    with ZipFile(zip_path) as archive:
        for row in _records(archive,"3_1_Generator_Y2024.xlsx","Operable"):
            pid=_id(row.get("Plant Code"))
            if pid not in IDS or row.get("Status")!="OP":
                continue
            if str(row.get("Technology") or "").strip()!="Onshore Wind Turbine":
                continue
            year=row.get("Operating Year");month=row.get("Operating Month")
            if year is None or month is None: raise ValueError(f"missing vintage {pid}")
            if (int(year),int(month))>(2024,12):
                raise ValueError(f"future operating date in 2024 OP: {pid}")
            groups[pid].append({"generator_id":str(row.get("Generator ID") or "").strip(),
                                "nameplate_mw":float(row["Nameplate Capacity (MW)"]),
                                "operating_year":int(year),"operating_month":int(month)})
    sites=[]
    for pid in IDS:
        rows=groups[pid]
        if not rows: raise ValueError(f"no 2024 operating wind generators for {pid}")
        sites.append({"plant_id":pid,"generator_count":len(rows),
                      "nameplate_mw":round(sum(r["nameplate_mw"] for r in rows),6),
                      "generator_records":sorted(rows,key=lambda x:x["generator_id"])})
    report={"year":2024,"source":"EIA-860 2024 Operable generator workbook",
            "sites":sites,"2024_year_end_nameplate_is_not_verified_monthly_capacity":True,
            "generator_count_is_not_turbine_count":True,
            "2024_monthly_capacity_factor_approved":False,
            "empirical_dispatch_approved":False}
    p=Path(output_path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EIA860_2024_WIND_CAPACITY="+json.dumps(report,sort_keys=True))
    return report

def main():
    audit("outputs/eia860/2024/eia8602024.zip",
          "outputs/spatial_weather_merged_2025/eia860_2024_wind_capacity.json")

if __name__=="__main__":main()
