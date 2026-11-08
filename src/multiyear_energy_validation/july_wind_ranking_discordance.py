"""Audit ranking discordance between July NASA POWER WS10M and observed net CF.

Three sites are a diagnostic case study, not a correlation inference.
"""
import json
from itertools import combinations
from pathlib import Path


def audit_ranking(context):
    sites=context["sites"]
    if len(sites)!=3 or {str(s["plant_id"]) for s in sites}!={"57484","57514","7526"}:
        raise ValueError("unexpected wind site cohort")
    pairs=[]
    for a,b in combinations(sorted(sites,key=lambda s:str(s["plant_id"])),2):
        wind_delta=a["nasa_power_ws10m_mean_ms"]-b["nasa_power_ws10m_mean_ms"]
        cf_delta=a["observed_july_net_capacity_factor"]-b["observed_july_net_capacity_factor"]
        pairs.append({"plant_ids":[str(a["plant_id"]),str(b["plant_id"])],
                      "ws10m_difference_ms":round(wind_delta,6),
                      "observed_cf_difference_percentage_points":round(100*cf_delta,4),
                      "opposite_rank_order":wind_delta*cf_delta<0})
    target=next(s for s in sites if str(s["plant_id"])=="7526")
    peer=next(s for s in sites if str(s["plant_id"])=="57514")
    return {"month":"2025-07","source_weather":"NASA POWER WS10M hourly",
            "source_generation":"EIA-923 July net generation / EIA-860 nameplate",
            "site_count":3,"pairwise_comparisons":pairs,
            "opposite_rank_order_pair_count":sum(p["opposite_rank_order"] for p in pairs),
            "solano_vs_57514_abs_mean_ws10m_difference_ms":round(abs(target["nasa_power_ws10m_mean_ms"]-peer["nasa_power_ws10m_mean_ms"]),6),
            "solano_vs_57514_abs_cf_difference_percentage_points":round(100*abs(target["observed_july_net_capacity_factor"]-peer["observed_july_net_capacity_factor"]),4),
            "wind_at_10m_not_hub_height":True,
            "ranking_is_not_causal_attribution":True,
            "no_inference_of_turbine_efficiency":True,
            "empirical_dispatch_approved":False}


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    data=json.loads((root/"july_wind_weather_generation_context.json").read_text(encoding="utf-8"))
    result=audit_ranking(data)
    (root/"july_wind_ranking_discordance.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("JULY_WIND_RANKING_DISCORDANCE="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
