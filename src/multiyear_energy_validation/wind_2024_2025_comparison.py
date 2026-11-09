"""Compare independent 2024 and 2025 wind–generation association diagnostics.

Descriptive only: no forecast, hourly availability, or causal inference.
"""
import json
from pathlib import Path

FIELDS=("monthly_mean_ws10m_vs_daily_normalized_generation_pearson",
        "monthly_mean_ws10m_cubed_vs_daily_normalized_generation_pearson")
DIFF_FIELDS=("delta_mean_ws10m_vs_delta_daily_generation_pearson",
             "delta_mean_ws10m_cubed_vs_delta_daily_generation_pearson")

def compare(rep2024,level2025,diff2025):
    if rep2024.get("year")!=2024: raise ValueError("2024 source year mismatch")
    a={str(s["plant_id"]):s for s in rep2024["level"]["sites"]}
    b={str(s["plant_id"]):s for s in level2025["sites"]}
    c={str(s["plant_id"]):s for s in rep2024["first_difference"]["sites"]}
    d={str(s["plant_id"]):s for s in diff2025["sites"]}
    if not (set(a)==set(b)==set(c)==set(d)=={"57484","57514","7526"}):
        raise ValueError("cohort mismatch")
    sites=[]
    for pid in sorted(a):
        metrics={}
        for field in FIELDS:
            v24=a[pid][field];v25=b[pid][field]
            metrics[field]={"2024":v24,"2025":v25,"delta_2025_minus_2024":round(v25-v24,6)}
        for field in DIFF_FIELDS:
            v24=c[pid][field];v25=d[pid][field]
            metrics[field]={"2024":v24,"2025":v25,"delta_2025_minus_2024":round(v25-v24,6)}
        sites.append({"plant_id":pid,"metrics":metrics})
    return {"years":[2024,2025],"sites":sites,"monthly_points_per_year":12,
            "first_difference_pairs_per_year":11,
            "independent_year_replication_not_out_of_sample_forecast":True,
            "wind_speed_is_10m_not_hub_height":True,
            "capacity_and_curtailment_not_controlled":True,
            "empirical_dispatch_approved":False}

def main():
    root=Path("outputs/spatial_weather_merged_2025")
    read=lambda name:json.loads((root/name).read_text(encoding="utf-8"))
    result=compare(read("annual_wind_2024_independent_replication.json"),
                   read("annual_wind_monthly_alignment_diagnostics.json"),
                   read("annual_wind_first_difference_sensitivity.json"))
    (root/"wind_2024_2025_comparison.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("WIND_2024_2025_COMPARISON="+json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
