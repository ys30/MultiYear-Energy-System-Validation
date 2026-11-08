"""Compare within-year observed generation seasonality across five sites.

Ratios are dimensionless relative to each site's own 2025 mean monthly MWh.
They are not capacity factors or weather-driven predictions.
"""
import json
from pathlib import Path

MONTHS=("january","february","march","april","may","june","july","august",
        "september","october","november","december")


def summarize_monthly_shapes(data):
    output=[]
    for site in data["sites"]:
        monthly=site["monthly_net_generation_mwh"]
        values=[monthly[m] for m in MONTHS]
        if any(v is None or v<0 for v in values):
            raise ValueError(f"missing/negative monthly generation: {site['plant_id']}")
        mean=sum(values)/12
        if mean<=0: raise ValueError(f"zero annual output: {site['plant_id']}")
        summer=sum(monthly[m] for m in ("june","july","august"))
        winter=sum(monthly[m] for m in ("december","january","february"))
        output.append({
            "plant_id":site["plant_id"],"fuel_code":site["fuel_code"],
            "annual_net_generation_mwh":round(sum(values),3),
            "july_relative_to_mean_month":round(monthly["july"]/mean,6),
            "june_august_net_generation_mwh":round(summer,3),
            "december_february_net_generation_mwh":round(winter,3),
            "summer_to_winter_generation_ratio":round(summer/winter,6) if winter>0 else None,
            "monthly_generation_relative_to_mean":{
                month:round(monthly[month]/mean,6) for month in MONTHS},
        })
    return {"source":"EIA-923 Page 1 2025 monthly net generation",
            "sites":output,
            "within_year_descriptive_comparison_only":True,
            "no_causal_weather_attribution":True,
            "not_capacity_factor":True,
            "not_hourly_availability":True,
            "empirical_dispatch_approved":False}


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    data=json.loads((root/"eia923_five_site_monthly_context.json").read_text(encoding="utf-8"))
    report=summarize_monthly_shapes(data)
    (root/"eia923_five_site_monthly_shape_comparison.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_MONTHLY_SHAPE_COMPARISON="+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
