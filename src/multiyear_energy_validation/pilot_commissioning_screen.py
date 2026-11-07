"""Check EIA-860 generator operating dates against the July 2025 weather pilot.

Annual 2025 OP status is not proof of operation during July 2025.
Missing commissioning dates are unknown, not evidence of operation.
"""
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from .eia860_fleet import _id, _records
from .eia860_renewable_geo import TECHNOLOGIES


def _month(value):
    try:
        number = int(value)
        return number if 1 <= number <= 12 else None
    except (TypeError, ValueError):
        return None


def _year(value):
    try:
        number = int(value)
        return number if 1900 <= number <= 2100 else None
    except (TypeError, ValueError):
        return None


def screen_pilot_chronology(archive_path, manifest_path, output_path, year=2025, month=7):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    sites = {(str(s["plant_id"]), s["technology"]) for s in manifest["sites"]}
    records = defaultdict(list)
    with ZipFile(archive_path) as archive:
        for r in _records(archive, f"3_1_Generator_Y{year}.xlsx", "Operable"):
            plant = _id(r.get("Plant Code"))
            tech = TECHNOLOGIES.get(str(r.get("Technology") or "").strip())
            if (plant, tech) not in sites or str(r.get("Status") or "").strip() != "OP":
                continue
            op_year = _year(r.get("Operating Year"))
            op_month = _month(r.get("Operating Month"))
            if op_year is None or op_month is None:
                decision = "unknown_operating_date"
            elif (op_year, op_month) > (year, month):
                decision = "commissioned_after_pilot_month"
            else:
                decision = "commissioned_by_pilot_month_per_eia860"
            records[(plant,tech)].append({
                "generator_id": str(r.get("Generator ID") or "").strip(),
                "nameplate_mw": float(r.get("Nameplate Capacity (MW)") or 0),
                "operating_year": op_year, "operating_month": op_month,
                "chronology_status": decision,
            })
    result = []
    for plant, tech in sorted(sites):
        generators = records[(plant,tech)]
        if not generators:
            raise ValueError(f"no OP generators for {plant}")
        by_status = defaultdict(float)
        for g in generators:
            by_status[g["chronology_status"]] += g["nameplate_mw"]
        eligible = bool(generators) and all(
            g["chronology_status"] == "commissioned_by_pilot_month_per_eia860"
            for g in generators
        )
        result.append({
            "plant_id": plant, "technology": tech,
            "generators": generators,
            "nameplate_mw_by_chronology_status": dict(sorted(by_status.items())),
            "all_2025_op_generators_commissioned_by_2025_07": eligible,
            "independent_july_generation_verified": False,
            "july_2025_operating_validation_approved": False,
        })
    output = {
        "reference_month": f"{year}-{month:02d}",
        "source": "EIA-860 2025 Operable generator Operating Year/Month",
        "annual_op_status_does_not_imply_july_operation": True,
        "sites": result,
        "all_sites_chronology_pass": all(x["all_2025_op_generators_commissioned_by_2025_07"] for x in result),
        "empirical_dispatch_approved": False,
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("SIX_SITE_CHRONOLOGY_SCREEN="+json.dumps({
        "reference_month": output["reference_month"],
        "sites": [{"plant_id":x["plant_id"],"technology":x["technology"],
                   "nameplate_mw_by_chronology_status":x["nameplate_mw_by_chronology_status"],
                   "all_generators_commissioned_by_pilot_month":x["all_2025_op_generators_commissioned_by_2025_07"]}
                  for x in result],
        "all_sites_chronology_pass": output["all_sites_chronology_pass"],
        "empirical_dispatch_approved": False,
    },sort_keys=True))
    return output


if __name__ == "__main__":
    screen_pilot_chronology(
        "outputs/eia860/2025/eia8602025.zip",
        "outputs/spatial_weather_pilot_2025/manifest.json",
        "outputs/spatial_weather_merged_2025/eia860_july2025_commissioning_screen.json",
    )
