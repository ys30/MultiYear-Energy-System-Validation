"""Annual 2025 NASA POWER WS10M versus EIA-923 monthly wind generation.

Diagnostic weather proxy only: no hub-height conversion, turbine power curve,
hourly availability, or causal weather-to-generation claim.
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .power_weather_pilot import fetch_power_hourly

WIND_IDS=("57484","57514","7526")
MONTHS=("january","february","march","april","may","june","july","august",
        "september","october","november","december")


def monthly_wind_weather(rows):
    groups=defaultdict(list)
    for r in rows:
        if r["wind_speed_10m_ms"]=="":
            raise ValueError("missing NASA POWER WS10M")
        stamp=datetime.strptime(r["period_utc"],"%Y-%m-%dT%H")
        if stamp.year!=2025: raise ValueError("unexpected weather year")
        ws=float(r["wind_speed_10m_ms"])
        if not 0<=ws<=100: raise ValueError("invalid WS10M")
        groups[stamp.month].append(ws)
    if len(rows)!=8760 or len({r["period_utc"] for r in rows})!=8760:
        raise ValueError("incomplete 2025 UTC hours")
    expected=[744,672,744,720,744,720,744,744,720,744,720,744]
    if [len(groups[m]) for m in range(1,13)]!=expected:
        raise ValueError("incomplete monthly weather coverage")
    return {MONTHS[m-1]:{
        "hour_count":len(groups[m]),
        "ws10m_mean_ms":round(sum(groups[m])/len(groups[m]),6),
        "ws10m_mean_cubed_ms3":round(sum(x**3 for x in groups[m])/len(groups[m]),6)}
        for m in range(1,13)}


def audit_annual_wind(manifest_path,generation_path,output_path):
    manifest=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    generation=json.loads(Path(generation_path).read_text(encoding="utf-8"))
    weather_sites={str(s["plant_id"]):s for s in manifest["sites"]}
    observed={str(s["plant_id"]):s for s in generation["sites"]}
    result=[]
    for pid in WIND_IDS:
        site=weather_sites[pid]
        if site["technology"]!="wind": raise ValueError("wrong site technology")
        monthly=monthly_wind_weather(fetch_power_hourly(
            site["latitude"],site["longitude"],"20250101","20251231"))
        gen=observed[pid]["monthly_net_generation_mwh"]
        for month in MONTHS:
            monthly[month]["observed_net_generation_mwh"]=gen[month]
            if gen[month] is None: raise ValueError("missing observed generation")
        result.append({"plant_id":pid,"latitude":site["latitude"],
                       "longitude":site["longitude"],"months":monthly})
    report={"year":2025,"sites":result,"source_weather":"NASA POWER hourly point WS10M UTC",
            "source_generation":"EIA-923 Page 1 2025 monthly net generation",
            "observed_generation_is_not_availability":True,
            "hub_height_wind_not_validated":True,
            "weather_to_generation_causality_not_established":True,
            "empirical_dispatch_approved":False}
    dest=Path(output_path);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ANNUAL_WIND_WEATHER_GENERATION="+json.dumps({
        "sites":[{"plant_id":s["plant_id"],"months":s["months"]} for s in result],
        "empirical_dispatch_approved":False},sort_keys=True))
    return report


if __name__=="__main__":
    audit_annual_wind("outputs/spatial_weather_pilot_2025/manifest.json",
                      "outputs/spatial_weather_merged_2025/eia923_five_site_monthly_context.json",
                      "outputs/spatial_weather_merged_2025/annual_wind_weather_generation_2025.json")
