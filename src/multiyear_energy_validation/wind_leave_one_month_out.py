"""Leave-one-month-out sensitivity for observed wind–generation associations.

Descriptive robustness, not model cross-validation or forecasting.
"""
import calendar
import json
from pathlib import Path
from .annual_wind_monthly_alignment import MONTHS,pearson

IDS=("57484","57514","7526")

def audit(reports):
    out=[]
    for year in (2024,2025):
        report=reports[year]
        if report["year"]!=year:raise ValueError("year mismatch")
        sites={str(s["plant_id"]):s for s in report["sites"]}
        if set(sites)!=set(IDS):raise ValueError("wind cohort mismatch")
        for pid in IDS:
            months=sites[pid]["months"]
            if set(months)!=set(MONTHS):raise ValueError("incomplete monthly records")
            wind=[float(months[m]["ws10m_mean_ms"]) for m in MONTHS]
            gen=[float(months[m]["observed_net_generation_mwh"])/calendar.monthrange(year,i+1)[1]
                 for i,m in enumerate(MONTHS)]
            full=pearson(wind,gen)
            leave=[]
            for i,m in enumerate(MONTHS):
                x=[v for j,v in enumerate(wind) if j!=i]
                y=[v for j,v in enumerate(gen) if j!=i]
                leave.append({"excluded_month":m,"pearson_r":pearson(x,y)})
            valid=[v["pearson_r"] for v in leave if v["pearson_r"] is not None]
            if len(valid)!=12 or full is None:raise ValueError("undefined sensitivity correlation")
            out.append({"year":year,"plant_id":pid,"full_12_month_r":full,
                        "leave_one_month_out_min_r":min(valid),
                        "leave_one_month_out_max_r":max(valid),
                        "largest_absolute_r_change":round(max(abs(v-full) for v in valid),6),
                        "leave_one_month_out":leave})
    return {"sites":out,"method":"leave-one-calendar-month-out Pearson sensitivity",
            "not_out_of_sample_forecast":True,
            "seasonal_confounding_not_eliminated":True,
            "hub_height_wind_not_validated":True,
            "empirical_dispatch_approved":False}

def main():
    root=Path("outputs/spatial_weather_merged_2025")
    reports={year:json.loads((root/f"annual_wind_weather_generation_{year}.json").read_text(encoding="utf-8"))
             for year in (2024,2025)}
    result=audit(reports)
    (root/"wind_2024_2025_leave_one_month_out.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("WIND_LEAVE_ONE_MONTH_OUT="+json.dumps({
        "sites":[{k:s[k] for k in ("year","plant_id","full_12_month_r",
            "leave_one_month_out_min_r","leave_one_month_out_max_r","largest_absolute_r_change")}
            for s in result["sites"]],
        "not_out_of_sample_forecast":True},sort_keys=True))

if __name__=="__main__":main()
