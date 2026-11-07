"""Derive a July 2025 commissioning-screened validation cohort.

This is only a chronology eligibility filter, not independent generation
verification or permission to run empirical dispatch.
"""
import json
from pathlib import Path


def select_commissioned_sites(chronology):
    eligible = []
    excluded = []
    for site in chronology["sites"]:
        record = {
            "plant_id": site["plant_id"],
            "technology": site["technology"],
            "nameplate_mw_by_chronology_status": site["nameplate_mw_by_chronology_status"],
            "independent_generation_verified": False,
            "empirical_availability_approved": False,
        }
        if site["all_2025_op_generators_commissioned_by_2025_07"]:
            eligible.append(record)
        else:
            record["reason"] = "one_or_more_generators_not_commissioned_by_2025_07"
            excluded.append(record)
    if len(eligible) + len(excluded) != len(chronology["sites"]):
        raise AssertionError("cohort conservation failed")
    return {
        "reference_month": "2025-07",
        "eligibility_basis": "EIA-860 2025 generator operating year/month only",
        "chronology_screened_sites": eligible,
        "excluded_from_july_operating_validation": excluded,
        "chronology_screened_count": len(eligible),
        "excluded_count": len(excluded),
        "independent_generation_verified": False,
        "renewable_availability_approved": False,
        "empirical_dispatch_approved": False,
    }


def main():
    root = Path("outputs/spatial_weather_merged_2025")
    chronology = json.loads((root/"eia860_july2025_commissioning_screen.json").read_text(encoding="utf-8"))
    result = select_commissioned_sites(chronology)
    (root/"july2025_commissioning_screened_cohort.json").write_text(
        json.dumps(result, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("JULY2025_COMMISSIONING_COHORT="+json.dumps({
        "eligible_plant_ids": [x["plant_id"] for x in result["chronology_screened_sites"]],
        "excluded_plant_ids": [x["plant_id"] for x in result["excluded_from_july_operating_validation"]],
        "chronology_screened_count": result["chronology_screened_count"],
        "excluded_count": result["excluded_count"],
        "independent_generation_verified": False,
        "empirical_dispatch_approved": False,
    },sort_keys=True))


if __name__ == "__main__":
    main()
