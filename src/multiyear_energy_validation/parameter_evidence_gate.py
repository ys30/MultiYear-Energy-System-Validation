"""Evidence-gated engineering parameter updates for real renewable plants.

A claimed value is never promoted to verified without a source, a directly
identifiable source locator, the applicable equipment/vintage, and a reviewer.
Scenario assumptions remain scenarios, not observed plant configurations.
"""
import json
from copy import deepcopy
from pathlib import Path

ALLOWED = {"unknown", "scenario_assumption", "documented_plant_specific"}
REQUIRED_EVIDENCE = ("source_title", "source_url", "source_locator",
                     "equipment_applicability", "effective_year", "reviewer")


def apply_parameter_evidence(registry, updates):
    result = deepcopy(registry)
    sites = {(s["plant_id"], s["technology"]): s for s in result["sites"]}
    seen = set()
    for item in updates:
        key = (str(item["plant_id"]), item["technology"])
        parameter = item["parameter"]
        identity = (*key, parameter)
        if identity in seen:
            raise ValueError("duplicate parameter evidence update")
        seen.add(identity)
        if key not in sites or parameter not in sites[key]["engineering_parameters"]:
            raise ValueError("unknown plant or engineering parameter")
        status = item.get("status")
        if status not in ALLOWED or status == "unknown":
            raise ValueError("update must be scenario_assumption or documented_plant_specific")
        if item.get("value") in (None, "") or item.get("unit") in (None, ""):
            raise ValueError("parameter value and unit required")
        evidence = item.get("evidence") or {}
        if status == "documented_plant_specific":
            missing = [field for field in REQUIRED_EVIDENCE if evidence.get(field) in (None, "")]
            if missing:
                raise ValueError("incomplete plant-specific evidence: "+",".join(missing))
            if not str(evidence["source_url"]).startswith(("https://", "http://")):
                raise ValueError("evidence source must have an absolute URL")
        sites[key]["engineering_parameters"][parameter] = {
            "value": item["value"], "unit": item["unit"], "source": evidence or None,
            "status": status,
        }
    result["parameter_evidence_review_complete"] = False
    result["renewable_availability_approved"] = False
    result["empirical_dispatch_approved"] = False
    return result


def export_evidence_template(registry_path, destination):
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    template = []
    for site in registry["sites"]:
        for parameter in site["engineering_parameters"]:
            template.append({
                "plant_id": site["plant_id"], "technology": site["technology"],
                "parameter": parameter, "value": None, "unit": None,
                "status": "unknown",
                "evidence": {key: None for key in REQUIRED_EVIDENCE},
            })
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("PLANT_PARAMETER_EVIDENCE_TEMPLATE="+json.dumps({
        "site_count": len(registry["sites"]), "parameter_slots": len(template),
        "verified_parameter_count": 0, "dispatch_approved": False,
    },sort_keys=True))
    return template


if __name__ == "__main__":
    export_evidence_template(
        "outputs/spatial_weather_merged_2025/plant_parameter_provenance.json",
        "outputs/spatial_weather_merged_2025/plant_parameter_evidence_template.json",
    )
