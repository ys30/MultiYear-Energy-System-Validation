"""Acquire official 2024 EIA-923 and independently extract monthly wind generation.

The 2024 cohort and nameplate chronology require a separate validation gate.
"""
import json
from pathlib import Path
from urllib.request import Request,urlopen
from shutil import copyfileobj
from zipfile import is_zipfile
from .eia923_monthly_context import audit_annual_months

URL_2024="https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip"

def main():
    archive=Path("outputs/eia923/2024/f923_2024.zip")
    archive.parent.mkdir(parents=True,exist_ok=True)
    with urlopen(Request(URL_2024,headers={"User-Agent":"Research validation (public EIA data)"}),timeout=120) as response,archive.open("wb") as stream:
        copyfileobj(response,stream)
    if not is_zipfile(archive):
        raise ValueError(f"Official EIA-923 2024 response is not a ZIP: {URL_2024}")
    output="outputs/spatial_weather_merged_2025/eia923_five_site_monthly_context_2024.json"
    result=audit_annual_months(archive,output,year=2024)
    wind=[s for s in result["sites"] if s["fuel_code"]=="WND"]
    if {s["plant_id"] for s in wind}!={"57484","57514","7526"}:
        raise ValueError("unexpected wind cohort")
    print("EIA923_2024_INDEPENDENT_WIND_MONTHS="+json.dumps({
        "year":2024,"sites":[{"plant_id":s["plant_id"],
        "months_reported":sum(v is not None for v in s["monthly_net_generation_mwh"].values()),
        "annual_net_generation_mwh":sum(v for v in s["monthly_net_generation_mwh"].values() if v is not None)}
        for s in wind],
        "2024_capacity_chronology_reviewed":False,
        "weather_to_generation_2024_replicated":False,
        "empirical_dispatch_approved":False},sort_keys=True))

if __name__=="__main__":
    main()
