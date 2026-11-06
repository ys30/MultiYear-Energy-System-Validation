import pytest
from multiyear_energy_validation.parameter_evidence_gate import apply_parameter_evidence


def registry():
    return {"sites":[{"plant_id":"123","technology":"wind",
                       "engineering_parameters":{"hub_height_m":{"value":None,"status":"unknown"}}}],
            "empirical_dispatch_approved":False}


def test_scenario_never_promoted_to_verified():
    result = apply_parameter_evidence(registry(), [
        {"plant_id":"123","technology":"wind","parameter":"hub_height_m",
         "value":100,"unit":"m","status":"scenario_assumption"}
    ])
    assert result["sites"][0]["engineering_parameters"]["hub_height_m"]["status"] == "scenario_assumption"
    assert not result["empirical_dispatch_approved"]


def test_unsubstantiated_verified_claim_rejected():
    with pytest.raises(ValueError, match="incomplete plant-specific evidence"):
        apply_parameter_evidence(registry(), [
            {"plant_id":"123","technology":"wind","parameter":"hub_height_m",
             "value":100,"unit":"m","status":"documented_plant_specific",
             "evidence":{"source_title":"generic wind farm overview"}}
        ])


def test_duplicate_parameter_updates_rejected():
    update = {"plant_id":"123","technology":"wind","parameter":"hub_height_m",
              "value":100,"unit":"m","status":"scenario_assumption"}
    with pytest.raises(ValueError,match="duplicate"):
        apply_parameter_evidence(registry(),[update,update])


def test_complete_evidence_keeps_dispatch_blocked():
    evidence = {k:"2025" for k in ("source_title","source_locator",
                                  "equipment_applicability","effective_year","reviewer")}
    evidence["source_url"] = "https://example.org/source"
    result = apply_parameter_evidence(registry(), [
        {"plant_id":"123","technology":"wind","parameter":"hub_height_m",
         "value":100,"unit":"m","status":"documented_plant_specific","evidence":evidence}
    ])
    assert result["sites"][0]["engineering_parameters"]["hub_height_m"]["status"] == "documented_plant_specific"
    assert not result["empirical_dispatch_approved"]
