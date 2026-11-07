"""Audit EIA-923 July net generation against EIA-860 nameplate, not availability.

Page 1 plant-fuel generation is a distinct aggregation from Page 4.
Capacity factor is descriptive and is not hourly renewable availability.
"""
import json
import math
from pathlib import Path

CAPACITY_MW = {"57373":347.7,"57695":585.9,"57484":189.0,"57514":265.4,"7526":300.5}
EXPECTED_FUEL = {"57373":"SUN","57695":"SUN","57484":"WND","57514":"WND","7526":"WND"}
HOURS = 31*24


def audit_monthly_factors(extracted):
    if extracted.get("month") != 7 or extracted.get("year") != 2025:
        raise ValueError("expected July 2025")
    if set(extracted["commissioning_screened_plant_ids"]) != set(CAPACITY_MW):
        raise ValueError("unexpected cohort")
    result=[]
    for pid in sorted(CAPACITY_MW):
        page1=[r for r in extracted["rows"] if r["plant_id"]==pid and
               r["source_sheet"]=="Page 1 Generation and Fuel Data"]
        if len(page1)!=1:
            raise ValueError(f"ambiguous or absent plant-fuel observations for {pid}: {len(page1)}")
        record=page1[0]
        if record["fuel_code"]!=EXPECTED_FUEL[pid]:
            raise ValueError(f"unexpected fuel for {pid}")
        mwh=record["net_generation_july_mwh"]
        if mwh is None or not math.isfinite(mwh) or mwh < 0:
            raise ValueError(f"invalid net generation for {pid}")
        cf=mwh/(CAPACITY_MW[pid]*HOURS)
        if cf>1+1e-9:
            raise ValueError(f"physical capacity-factor bound exceeded for {pid}")
        result.append({
            "plant_id":pid,"fuel_code":record["fuel_code"],
            "nameplate_mw":CAPACITY_MW[pid],"net_generation_mwh":mwh,
            "july_hours":HOURS,"monthly_net_capacity_factor":round(cf,6),
            "eia923_source_sheet":record["source_sheet"],
            "eia923_source_row":record["source_row"],
            "monthly_net_capacity_factor_is_not_availability":True,
        })
    totals={}
    for fuel in ("SUN","WND"):
        group=[r for r in result if r["fuel_code"]==fuel]
        mw=sum(r["nameplate_mw"] for r in group)
        mwh=sum(r["net_generation_mwh"] for r in group)
        totals[fuel]={"nameplate_mw":round(mw,6),"net_generation_mwh":mwh,
                      "capacity_weighted_monthly_net_capacity_factor":round(mwh/(mw*HOURS),6)}
    return {"reference_month":"2025-07","source":"EIA-923 2025 Page 1; EIA-860 2025 OP nameplate",
            "sites":result,"technology_totals":totals,
            "independent_generation_observed":True,
            "equipment_parameters_validated":False,
            "hourly_renewable_availability_approved":False,
            "empirical_dispatch_approved":False}


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    extracted=json.loads((root/"eia923_july2025_five_site_extract.json").read_text(encoding="utf-8"))
    result=audit_monthly_factors(extracted)
    (root/"eia923_july2025_capacity_factor_audit.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_JULY_CAPACITY_FACTOR_AUDIT="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
