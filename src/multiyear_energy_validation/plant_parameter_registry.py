"""Conservative provenance registry for six pilot plants.

EIA-860 generator records support technology and nameplate only. Unknown
engineering parameters must remain null; no default equipment assumptions.
"""
import json
from pathlib import Path

SOLAR_PARAMETERS = ("tilt_deg", "azimuth_deg", "dc_ac_ratio", "inverter_efficiency",
                    "temperature_coefficient", "module_temperature_model", "system_losses")
WIND_PARAMETERS = ("hub_height_m", "roughness_length_m", "turbine_power_curve",
                   "rated_power_mw", "wake_losses", "electrical_losses")


def build_registry(technology_audit):
    entries = []
    for site in technology_audit["sites"]:
        group = site["group"]
        if group not in ("solar", "wind"):
            raise ValueError("unsupported generator technology")
        if group == "solar" and not site["pv_only_technology"]:
            raise ValueError("non-PV technology cannot enter PV registry")
        if group == "wind" and not site["wind_only_technology"]:
            raise ValueError("non-wind technology cannot enter wind registry")
        parameters = SOLAR_PARAMETERS if group == "solar" else WIND_PARAMETERS
        entries.append({
            "plant_id": site["plant_id"], "technology": group,
            "eia_2025_nameplate_mw": site["total_nameplate_mw"],
            "eia_2025_generator_count": site["generator_count"],
            "eia_technology": site["eia_technology_nameplate_mw"],
            "verified_fields": {
                "technology": {"source": "EIA-860 2025 Operable generator Technology",
                               "status": "verified_generator_classification"},
                "nameplate_mw": {"source": "EIA-860 2025 Operable generator Nameplate Capacity (MW)",
                                 "status": "verified_nameplate_not_ac_inverter_rating"},
            },
            "engineering_parameters": {
                key: {"value": None, "unit": None, "source": None, "status": "unknown"}
                for key in parameters
            },
            "independent_output_validation": {
                "source": None, "period": None, "status": "not_available"
            },
            "physical_model_approved": False,
        })
    return {
        "source": "EIA-860 2025 generator technology audit",
        "sites": sorted(entries, key=lambda x: (x["technology"], x["plant_id"])),
        "no_imputed_equipment_parameters": True,
        "renewable_availability_approved": False,
        "empirical_dispatch_approved": False,
    }


def export_registry(audit_path, output_path):
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    result = build_registry(audit)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("SIX_SITE_PARAMETER_REGISTRY="+json.dumps({
        "site_count": len(result["sites"]),
        "solar_sites": sum(x["technology"]=="solar" for x in result["sites"]),
        "wind_sites": sum(x["technology"]=="wind" for x in result["sites"]),
        "unknown_parameter_fields": sum(len(x["engineering_parameters"]) for x in result["sites"]),
        "no_imputed_equipment_parameters": True,
        "empirical_dispatch_approved": False,
    },sort_keys=True))
    return result


if __name__ == "__main__":
    export_registry(
        "outputs/spatial_weather_merged_2025/eia_generator_technology_audit.json",
        "outputs/spatial_weather_merged_2025/plant_parameter_provenance.json",
    )
