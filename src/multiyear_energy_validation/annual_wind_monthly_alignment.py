"""Descriptive within-plant monthly wind/weather alignment diagnostics.

Twelve monthly points per plant are not independent causal evidence.
"""
import json
import math
import calendar
from pathlib import Path

MONTHS=("january","february","march","april","may","june","july","august","september","october","november","december")

def pearson(a,b):
    if len(a)!=len(b) or len(a)<3: raise ValueError("invalid paired observations")
    am=sum(a)/len(a);bm=sum(b)/len(b)
    numerator=sum((x-am)*(y-bm) for x,y in zip(a,b))
    aa=sum((x-am)**2 for x in a);bb=sum((y-bm)**2 for y in b)
    if aa<=0 or bb<=0: return None
    return round(numerator/math.sqrt(aa*bb),6)

def summarize(report):
    results=[]
    for site in report["sites"]:
        monthly=site["months"]
        if set(monthly)!=set(MONTHS): raise ValueError("incomplete months")
        ws=[monthly[m]["ws10m_mean_ms"] for m in MONTHS]
        ws3=[monthly[m]["ws10m_mean_cubed_ms3"] for m in MONTHS]
        gen=[monthly[m]["observed_net_generation_mwh"] for m in MONTHS]
        if any(x is None or not math.isfinite(x) for x in ws+ws3+gen):
            raise ValueError("missing or invalid weather/generation")
        year=int(report.get('year',2025))
        days=[calendar.monthrange(year,m)[1] for m in range(1,13)]
        daily=[v/d for v,d in zip(gen,days)]
        results.append({"plant_id":site["plant_id"],
                        "monthly_mean_ws10m_vs_monthly_generation_pearson":pearson(ws,gen),
                        "monthly_mean_ws10m_vs_daily_normalized_generation_pearson":pearson(ws,daily),
                        "monthly_mean_ws10m_cubed_vs_daily_normalized_generation_pearson":pearson(ws3,daily),
                        "monthly_observation_count":12})
    return {"sites":results,"monthly_observations_per_plant":12,
            "daily_normalization_removes_month_length_only":True,
            "correlations_are_descriptive_not_causal":True,
            "weather_is_not_hub_height_wind":True,
            "weather_to_power_model_validated":False,
            "hourly_availability_approved":False,"empirical_dispatch_approved":False}

def main():
    root=Path("outputs/spatial_weather_merged_2025")
    report=json.loads((root/"annual_wind_weather_generation_2025.json").read_text(encoding="utf-8"))
    result=summarize(report)
    (root/"annual_wind_monthly_alignment_diagnostics.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ANNUAL_WIND_MONTHLY_ALIGNMENT="+json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
