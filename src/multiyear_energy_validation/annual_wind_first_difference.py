"""First-difference sensitivity for monthly wind/weather association.

Differences reduce common smooth seasonality but do not remove confounding.
No weather-to-power model or causal interpretation is approved.
"""
import json
from pathlib import Path
from .annual_wind_monthly_alignment import MONTHS, pearson

DAYS=(31,28,31,30,31,30,31,31,30,31,30,31)


def first_difference_audit(report):
    results=[]
    for site in report["sites"]:
        monthly=site["months"]
        if set(monthly)!=set(MONTHS):
            raise ValueError("incomplete annual monthly coverage")
        ws=[float(monthly[m]["ws10m_mean_ms"]) for m in MONTHS]
        ws3=[float(monthly[m]["ws10m_mean_cubed_ms3"]) for m in MONTHS]
        generation=[float(monthly[m]["observed_net_generation_mwh"])/d for m,d in zip(MONTHS,DAYS)]
        def diff(x): return [b-a for a,b in zip(x,x[1:])]
        results.append({
            "plant_id":str(site["plant_id"]),
            "first_difference_monthly_pairs":11,
            "delta_mean_ws10m_vs_delta_daily_generation_pearson":pearson(diff(ws),diff(generation)),
            "delta_mean_ws10m_cubed_vs_delta_daily_generation_pearson":pearson(diff(ws3),diff(generation)),
        })
    return {"sites":results,"source":"NASA POWER WS10M 2025 / EIA-923 Page 1 2025",
            "month_count":12,"first_difference_pairs":11,
            "first_differences_do_not_remove_all_seasonal_confounding":True,
            "not_an_out_of_sample_forecast":True,
            "not_causal":True,"hub_height_not_validated":True,
            "empirical_dispatch_approved":False}


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    report=json.loads((root/"annual_wind_weather_generation_2025.json").read_text(encoding="utf-8"))
    result=first_difference_audit(report)
    (root/"annual_wind_first_difference_sensitivity.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ANNUAL_WIND_FIRST_DIFFERENCE="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
