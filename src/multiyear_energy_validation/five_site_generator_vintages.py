"""Generator-level vintage and nameplate audit for July 2025 five-site cohort.

EIA-860 generator vintages and status are screening evidence, not
generator-specific EIA-923 generation or turbine models.
"""
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from .eia860_fleet import _id, _records
from .eia860_renewable_geo import TECHNOLOGIES


def generator_vintage_audit(zip_path, cohort_path, output_path):
    cohort=json.loads(Path(cohort_path).read_text(encoding="utf-8"))
    sites={str(s["plant_id"]):s["technology"] for s in cohort["chronology_screened_sites"]}
    groups=defaultdict(list)
    with ZipFile(zip_path) as archive:
        for row in _records(archive,"3_1_Generator_Y2025.xlsx","Operable"):
            pid=_id(row.get("Plant Code"))
            if pid not in sites or row.get("Status")!="OP":
                continue
            if TECHNOLOGIES.get(str(row.get("Technology") or "").strip())!=sites[pid]:
                continue
            groups[pid].append({
                "generator_id":str(row.get("Generator ID") or "").strip(),
                "nameplate_mw":float(row["Nameplate Capacity (MW)"]),
                "operating_year":row.get("Operating Year"),
                "operating_month":row.get("Operating Month"),
                "technology":str(row.get("Technology") or "").strip(),
            })
    result=[]
    for pid in sorted(sites):
        rows=sorted(groups[pid],key=lambda r:r["generator_id"])
        if not rows: raise ValueError(f"no generators for {pid}")
        result.append({
            "plant_id":pid,"technology":sites[pid],"generator_count":len(rows),
            "generator_nameplate_mw":round(sum(r["nameplate_mw"] for r in rows),6),
            "operating_years":sorted({str(r["operating_year"]) for r in rows}),
            "generators":rows,
            "generator_count_is_not_turbine_count":True,
            "generator_level_generation_matched":False,
        })
    report={"source":"EIA-860 2025 Operable generator sheet",
            "sites":result,"eia923_page1_plant_fuel_generation_not_generator_specific":True,
            "generator_level_generation_matched":False,
            "empirical_dispatch_approved":False}
    out=Path(output_path);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print("FIVE_SITE_GENERATOR_VINTAGES="+json.dumps({
        "sites":[{k:r[k] for k in ("plant_id","technology","generator_count","generator_nameplate_mw","operating_years")} for r in result],
        "generator_level_generation_matched":False,
    },sort_keys=True))
    return report


if __name__=="__main__":
    generator_vintage_audit(
        "outputs/eia860/2025/eia8602025.zip",
        "outputs/spatial_weather_merged_2025/july2025_commissioning_screened_cohort.json",
        "outputs/spatial_weather_merged_2025/five_site_generator_vintage_audit.json",
    )
