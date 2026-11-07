"""EIA-923 July generation intake: conservative generator-to-plant matching contract.

Input is a *reviewed* normalized monthly plant-generation CSV, not weather,
not EIA-930 balancing-authority generation, and not a capacity factor.
EIA-923 plant/fuel monthly data may combine generators and storage; this
module rejects ambiguous or nonpositive observations instead of imputing.
"""
import csv
import json
import math
from pathlib import Path

REQUIRED = ("plant_id", "year", "month", "net_generation_mwh",
            "fuel_code", "generation_source", "source_sheet", "source_row")


def _positive_finite(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def screen_eia923_monthly(rows, cohort):
    candidates = {str(s["plant_id"]): s for s in cohort["chronology_screened_sites"]}
    grouped = {pid: [] for pid in candidates}
    rejected = []
    for index, row in enumerate(rows, 1):
        if any(row.get(key) in (None, "") for key in REQUIRED):
            rejected.append({"row": index, "reason": "missing_required_provenance_or_value"})
            continue
        pid = str(row["plant_id"]).strip()
        if pid not in candidates:
            continue
        if str(row["year"]).strip() != "2025" or str(row["month"]).strip() not in ("7", "07"):
            continue
        generation = _positive_finite(row["net_generation_mwh"])
        if generation is None:
            rejected.append({"row": index, "plant_id": pid, "reason": "nonpositive_or_invalid_generation"})
            continue
        grouped[pid].append({
            "net_generation_mwh": generation,
            "fuel_code": str(row["fuel_code"]).strip(),
            "generation_source": row["generation_source"],
            "source_sheet": row["source_sheet"],
            "source_row": row["source_row"],
        })
    sites = []
    for pid, site in sorted(candidates.items()):
        entries = grouped[pid]
        # EIA-923 plant-fuel aggregation is not a plant-specific, uncensored
        # renewable availability measurement. Require manual fuel/asset review.
        sites.append({
            "plant_id": pid, "technology": site["technology"],
            "matching_rows": len(entries),
            "reported_net_generation_mwh_by_fuel": [
                {"fuel_code": r["fuel_code"], "net_generation_mwh": r["net_generation_mwh"],
                 "source_sheet": r["source_sheet"], "source_row": r["source_row"]}
                for r in entries
            ],
            "fuel_and_storage_attribution_reviewed": False,
            "monthly_generation_independently_validated": False,
            "hourly_available_generation_inferred": False,
        })
    return {
        "source_contract": "reviewed normalized EIA-923 2025 plant-fuel monthly generation",
        "month": "2025-07", "sites": sites, "rejected": rejected,
        "independent_monthly_validation_approved": False,
        "hourly_renewable_availability_approved": False,
        "empirical_dispatch_approved": False,
    }


def main():
    root = Path("outputs/spatial_weather_merged_2025")
    cohort = json.loads((root/"july2025_commissioning_screened_cohort.json").read_text(encoding="utf-8"))
    source = Path("inputs/eia923_2025_july_reviewed.csv")
    if source.exists():
        with source.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        state = "review_required"
    else:
        rows = []
        state = "awaiting_reviewed_source"
    result = screen_eia923_monthly(rows, cohort)
    result["source_state"] = state
    (root/"eia923_monthly_generation_screen.json").write_text(
        json.dumps(result, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("EIA923_MONTHLY_GENERATION_SCREEN="+json.dumps({
        "source_state":state, "cohort_count":len(result["sites"]),
        "matched_rows":sum(s["matching_rows"] for s in result["sites"]),
        "monthly_validation_approved":False, "empirical_dispatch_approved":False,
    },sort_keys=True))


if __name__ == "__main__":
    main()
