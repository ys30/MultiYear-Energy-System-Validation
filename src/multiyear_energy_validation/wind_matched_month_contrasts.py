"""Matched-calendar-month 2025-minus-2024 wind and generation contrasts.

Two annual observations per month; descriptive sensitivity, not causal.
"""
import calendar
import json
from pathlib import Path
from .annual_wind_monthly_alignment import MONTHS,pearson

IDS=("57484","57514","7526")

def audit(reports):
    sites={}
    for year in (2024,2025):
        report=reports[year]
        if report.get("year")!=year:raise ValueError("year mismatch")
        s={str(x["plant_id"]):x for x in report["sites"]}
        if set(s)!=set(IDS):raise ValueError("cohort mismatch")
        sites[year]=s
    results=[]
    for pid in IDS:
        delta_wind=[];delta_generation=[];rows=[]
        for i,m in enumerate(MONTHS):
            observations=[]
            for year in (2024,2025):
                month=sites[year][pid]["months"][m]
                days=calendar.monthrange(year,i+1)[1]
                observations.append((float(month["ws10m_mean_ms"]),
                    float(month["observed_net_generation_mwh"])/days))
            dw=observations[1][0]-observations[0][0]
            dg=observations[1][1]-observations[0][1]
            delta_wind.append(dw);delta_generation.append(dg)
            rows.append({"month":m,"delta_ws10m_2025_minus_2024_ms":round(dw,6),
                "delta_daily_generation_2025_minus_2024_mwh_per_day":round(dg,6)})
        results.append({"plant_id":pid,"matched_month_year_difference_pearson_r":
            pearson(delta_wind,delta_generation),"matched_calendar_months":12,
            "monthly_contrasts":rows})
    return {"years":[2024,2025],"sites":results,
        "method":"Pearson across 12 paired calendar-month 2025-minus-2024 contrasts",
        "only_two_years":True,"not_out_of_sample_forecast":True,
        "interannual_capacity_curtailment_and_maintenance_not_controlled":True,
        "empirical_dispatch_approved":False}

def main():
    root=Path("outputs/spatial_weather_merged_2025")
    reports={y:json.loads((root/f"annual_wind_weather_generation_{y}.json").read_text(encoding="utf-8"))
             for y in (2024,2025)}
    result=audit(reports)
    (root/"wind_2024_2025_matched_month_contrasts.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("WIND_MATCHED_MONTH_CONTRASTS="+json.dumps({
        "sites":[{"plant_id":s["plant_id"],"r":s["matched_month_year_difference_pearson_r"]}
                 for s in result["sites"]],"only_two_years":True},sort_keys=True))

if __name__=="__main__":main()
