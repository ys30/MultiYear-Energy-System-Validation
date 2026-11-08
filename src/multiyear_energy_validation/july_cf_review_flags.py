"""Document checks required before interpreting high observed July capacity factors.

A monthly factor is descriptive. It cannot establish turbine performance,
availability, curtailment, or the correctness of an hourly weather conversion.
"""
import json
from pathlib import Path


def flag_review_items(audit):
    records=[]
    for s in audit["sites"]:
        cf=s["monthly_net_capacity_factor"]
        flags=[]
        if cf>=0.5:
            flags.append("high_monthly_net_capacity_factor_review")
        if s["fuel_code"]=="WND":
            flags.append("verify_multi_generator_vintages_and_plant_capacity")
            flags.append("10m_weather_not_hub_height_wind")
        else:
            flags.append("verify_ac_dc_capacity_and_tracking_before_model_validation")
        flags.append("page1_plant_fuel_not_generator_level_attribution")
        records.append({
            "plant_id":s["plant_id"],"fuel_code":s["fuel_code"],
            "monthly_net_capacity_factor":cf,
            "review_flags":flags,
            "data_error_confirmed":False,
            "physical_model_validated":False,
        })
    return {"reference_month":"2025-07","review_records":records,
            "observed_generation_verified_at_plant_fuel_level":True,
            "generator_level_attribution_verified":False,
            "equipment_model_validation_approved":False,
            "hourly_availability_approved":False,
            "empirical_dispatch_approved":False}


def main():
    root=Path("outputs/spatial_weather_merged_2025")
    audit=json.loads((root/"eia923_july2025_capacity_factor_audit.json").read_text(encoding="utf-8"))
    result=flag_review_items(audit)
    (root/"july2025_capacity_factor_review_flags.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("JULY2025_CF_REVIEW_FLAGS="+json.dumps({
        "review_records":result["review_records"],
        "generator_level_attribution_verified":False,
        "empirical_dispatch_approved":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
