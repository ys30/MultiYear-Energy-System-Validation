"""Audit EIA-860 generator technology mix for the six weather-pilot plants.

Plant-level MW and technology labels must not be treated as verified PV module
or wind turbine specifications. This audit exposes within-plant technology mix.
"""
import json
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

from .eia860_fleet import _id, _records
from .eia860_renewable_geo import TECHNOLOGIES


def audit_selected_generator_technologies(archive_path, pilot_manifest, output_path):
    sites = json.loads(Path(pilot_manifest).read_text(encoding="utf-8"))["sites"]
    selected = {(str(s["plant_id"]), s["technology"]) for s in sites}
    rows = defaultdict(list)
    with ZipFile(archive_path) as archive:
        for r in _records(archive, "3_1_Generator_Y2025.xlsx", "Operable"):
            pid = _id(r.get("Plant Code"))
            technology = str(r.get("Technology") or "").strip()
            group = TECHNOLOGIES.get(technology)
            if (pid, group) not in selected or str(r.get("Status") or "").strip() != "OP":
                continue
            rows[(pid, group)].append({
                "generator_id": str(r.get("Generator ID") or "").strip(),
                "eia_technology": technology,
                "nameplate_mw": float(r.get("Nameplate Capacity (MW)") or 0),
            })
    result = []
    for pid, group in sorted(selected):
        generators = rows[(pid, group)]
        if not generators:
            raise ValueError(f"no OP generator found: {pid} {group}")
        by_tech = defaultdict(float)
        for g in generators:
            by_tech[g["eia_technology"]] += g["nameplate_mw"]
        result.append({
            "plant_id": pid, "group": group, "generator_count": len(generators),
            "eia_technology_nameplate_mw": dict(sorted(by_tech.items())),
            "total_nameplate_mw": round(sum(by_tech.values()), 6),
            "pv_only_technology": group == "solar" and set(by_tech) == {"Solar Photovoltaic"},
            "wind_only_technology": group == "wind" and set(by_tech) <= {
                "Onshore Wind Turbine", "Offshore Wind Turbine"},
            "module_turbine_inverter_specs_verified": False,
            "physical_power_model_approved": False,
        })
    output = {
        "source": "EIA-860 2025 operable generator technology labels",
        "sites": result, "equipment_parameters_verified": False,
        "empirical_dispatch_approved": False,
    }
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("SIX_SITE_EIA_TECH_AUDIT="+json.dumps(output, sort_keys=True))
    return output


if __name__ == "__main__":
    audit_selected_generator_technologies(
        "outputs/eia860/2025/eia8602025.zip",
        "outputs/spatial_weather_pilot_2025/manifest.json",
        "outputs/spatial_weather_merged_2025/eia_generator_technology_audit.json",
    )
