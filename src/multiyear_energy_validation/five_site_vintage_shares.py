"""Capacity-weighted commissioning vintage audit, not a turbine-model inference."""
import json
from collections import defaultdict
from pathlib import Path


def audit_vintage_shares(report):
    result=[]
    for site in report["sites"]:
        by_year=defaultdict(float)
        for gen in site["generators"]:
            year=int(gen["operating_year"])
            mw=float(gen["nameplate_mw"])
            if year>2025 or year<1900 or mw<=0:
                raise ValueError(f"invalid vintage/capacity: {site['plant_id']}")
            by_year[year]+=mw
        total=sum(by_year.values())
        if abs(total-site["generator_nameplate_mw"])>1e-4:
            raise ValueError(f"capacity reconciliation failed: {site['plant_id']}")
        vintages=[{"operating_year":year,"nameplate_mw":round(mw,4),
                   "capacity_share":round(mw/total,6)}
                  for year,mw in sorted(by_year.items())]
        result.append({"plant_id":site["plant_id"],"technology":site["technology"],
                       "nameplate_mw":total,"vintages":vintages,
                       "multiple_vintages":len(vintages)>1,
                       "vintage_specific_generation_known":False})
    return {"reference":"EIA-860 2025 operable generator records",
            "sites":result,"vintage_specific_generation_known":False,
            "vintage_specific_equipment_models_verified":False,
            "hourly_availability_approved":False,"empirical_dispatch_approved":False}


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    report=json.loads((root/"five_site_generator_vintage_audit.json").read_text(encoding="utf-8"))
    result=audit_vintage_shares(report)
    (root/"five_site_vintage_capacity_shares.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("FIVE_SITE_VINTAGE_CAPACITY_SHARES="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
