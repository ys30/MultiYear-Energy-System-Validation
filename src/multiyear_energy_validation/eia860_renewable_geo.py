"""Join official EIA-860 CISO plant coordinates to OP solar/wind generators."""
import csv
import json
from pathlib import Path
from zipfile import ZipFile

from .eia860_fleet import _id, _records
from .plant_weather_mapping_gate import audit_plant_capacity

TECHNOLOGIES = {
    "Solar Photovoltaic": "solar",
    "Solar Thermal with Energy Storage": "solar",
    "Solar Thermal without Energy Storage": "solar",
    "Onshore Wind Turbine": "wind",
    "Offshore Wind Turbine": "wind",
}


def extract_ciso_renewable_locations(archive_path, year, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plants = {}
    with ZipFile(archive_path) as archive:
        for row in _records(archive, f"2___Plant_Y{year}.xlsx", "Plant"):
            plant_id = _id(row.get("Plant Code"))
            if plant_id in plants:
                raise ValueError("duplicate plant identifier")
            plants[plant_id] = row
        candidates = []
        for row in _records(archive, f"3_1_Generator_Y{year}.xlsx", "Operable"):
            plant_id = _id(row.get("Plant Code"))
            plant = plants.get(plant_id)
            if plant is None or str(plant.get("Balancing Authority Code") or "").strip() != "CISO":
                continue
            technology = TECHNOLOGIES.get(str(row.get("Technology") or "").strip())
            if technology is None or str(row.get("Status") or "").strip() != "OP":
                continue
            candidates.append({
                "plant_id": plant_id,
                "generator_id": str(row.get("Generator ID") or "").strip(),
                "latitude": plant.get("Latitude"),
                "longitude": plant.get("Longitude"),
                "capacity_mw": row.get("Nameplate Capacity (MW)"),
                "technology": technology,
                "report_year": year,
                "operating_status": "OP",
                "ciso_membership_verified": True,
            })
    audit = audit_plant_capacity(candidates, year)
    fields = ("plant_id", "generator_id", "latitude", "longitude",
              "capacity_mw", "technology", "year")
    with (output / f"ciso_renewable_geocoded_{year}.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audit["accepted"])
    summary = {
        "year": year,
        "source": "EIA-860 official annual plant and operable generator workbooks",
        "ciso_membership_basis": "Plant Balancing Authority Code == CISO",
        "candidate_count": len(candidates),
        "accepted_count": audit["accepted_count"],
        "rejected_count": audit["rejected_count"],
        "accepted_capacity_mw": audit["accepted_capacity_mw"],
        "rejected_reasons": audit["rejected"],
        "geographic_weather_join_ready": audit["weather_capacity_mapping_approved"],
        "weather_coverage_validated": False,
        "renewable_availability_validated": False,
        "dispatch_approved": False,
    }
    (output / f"ciso_renewable_geocoded_{year}.manifest.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("EIA860_RENEWABLE_GEO=" + json.dumps({
        k: v for k, v in summary.items() if k != "rejected_reasons"
    }, sort_keys=True))
    return summary
