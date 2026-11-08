"""Pre-specified descriptive contrasts for five-site EIA-923 seasonal output.

This analysis quantifies differences in monthly generation shape. It does
not estimate causal weather effects or infer hourly availability.
"""
import json
from pathlib import Path


def seasonal_contrasts(report):
    by_id={s["plant_id"]:s for s in report["sites"]}
    if set(by_id)!={"57373","57695","57484","57514","7526"}:
        raise ValueError("unexpected five-site cohort")
    target=by_id["7526"]
    wind_peers=[by_id[p] for p in ("57484","57514")]
    solar=[by_id[p] for p in ("57373","57695")]
    peer_max=max(s["summer_to_winter_generation_ratio"] for s in wind_peers)
    if peer_max<=0: raise ValueError("invalid peer ratio")
    target_ratio=target["summer_to_winter_generation_ratio"]
    july_target=target["july_relative_to_mean_month"]
    july_peer_max=max(s["july_relative_to_mean_month"] for s in wind_peers)
    return {
        "target_plant_id":"7526",
        "wind_peer_plant_ids":["57484","57514"],
        "solar_comparator_plant_ids":["57373","57695"],
        "target_summer_winter_ratio":target_ratio,
        "peer_wind_max_summer_winter_ratio":peer_max,
        "target_to_peer_max_summer_winter_ratio":round(target_ratio/peer_max,6),
        "target_july_to_mean_month":july_target,
        "peer_wind_max_july_to_mean_month":july_peer_max,
        "target_july_relative_to_mean_exceeds_both_wind_peers":july_target>july_peer_max,
        "target_summer_winter_exceeds_both_wind_peers":target_ratio>peer_max,
        "source":"EIA-923 2025 monthly net generation",
        "interpretation":"descriptive observed generation shape; no causal attribution",
        "sample_size_months":12,
        "sample_size_wind_plants":3,
        "weather_resource_causality_established":False,
        "equipment_effect_established":False,
        "hourly_availability_approved":False,
        "empirical_dispatch_approved":False,
    }


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    report=json.loads((root/"eia923_five_site_monthly_shape_comparison.json").read_text(encoding="utf-8"))
    result=seasonal_contrasts(report)
    (root/"eia923_five_site_seasonal_contrasts.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_FIVE_SITE_SEASONAL_CONTRASTS="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
