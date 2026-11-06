"""Audit whether real-plant weather inputs can support a physical AC potential model.

A readiness audit is intentionally NOT a weather-to-power converter. It fails
closed when required physical and validation inputs are absent.
"""
import csv
import json
from pathlib import Path

REQUIRED_WEATHER = {
    "solar": ("ghi_wm2", "dni_wm2", "dhi_wm2", "air_temperature_c", "wind_speed_10m_ms"),
    "wind": ("wind_speed_10m_ms", "air_temperature_c", "surface_pressure_pa"),
}
REQUIRED_PLANT = {
    "solar": ("tilt_deg", "azimuth_deg", "dc_ac_ratio", "inverter_efficiency",
              "temperature_coefficient", "module_temperature_model", "system_losses"),
    "wind": ("hub_height_m", "roughness_length_m", "turbine_power_curve",
             "rated_power_mw", "wake_losses", "electrical_losses"),
}
REQUIRED_VALIDATION = ("independent_generation_or_resource_benchmark",
                       "outage_curtailment_treatment", "temporal_validation_window")


def assess_site(technology, weather_columns, plant_metadata=None, validation=None):
    if technology not in REQUIRED_WEATHER:
        raise ValueError("unsupported technology")
    plant_metadata = plant_metadata or {}
    validation = validation or {}
    missing_weather = sorted(set(REQUIRED_WEATHER[technology]) - set(weather_columns))
    missing_plant = sorted(key for key in REQUIRED_PLANT[technology]
                           if plant_metadata.get(key) in (None, ""))
    missing_validation = sorted(key for key in REQUIRED_VALIDATION
                                if validation.get(key) in (None, ""))
    return {
        "technology": technology,
        "missing_weather_variables": missing_weather,
        "missing_plant_parameters": missing_plant,
        "missing_independent_validation": missing_validation,
        "physical_conversion_ready": not (missing_weather or missing_plant or missing_validation),
        "empirical_dispatch_approved": False,
    }


def audit_six_site_weather(directory):
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    results = []
    for site in manifest["sites"]:
        path = root/f"{site['technology']}_plant_{site['plant_id']}_july2025.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames or []
            count = sum(1 for _ in reader)
        if count != 744:
            raise ValueError("expected 744 rows for each site")
        result = assess_site(site["technology"], columns)
        result["plant_id"] = site["plant_id"]
        result["hours"] = count
        results.append(result)
    output = {
        "period": "2025-07", "sites": results,
        "physical_conversion_ready": all(s["physical_conversion_ready"] for s in results),
        "independent_validation_completed": False,
        "renewable_availability_approved": False,
        "empirical_dispatch_approved": False,
        "purpose": "fail-closed physical model input and validation readiness audit",
    }
    (root/"physical_conversion_readiness.json").write_text(
        json.dumps(output, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print("PHYSICAL_CONVERSION_READINESS="+json.dumps(output,sort_keys=True))
    return output


if __name__ == "__main__":
    audit_six_site_weather("outputs/spatial_weather_pilot_2025")
