from multiyear_energy_validation.empirical_dispatch_readiness import assess_readiness, SYSTEM_GATES
import pytest

def sample(status="unknown",source=None):
    return {"sites":[{"plant_id":57484,"technology":"wind","engineering_parameters":{
        "hub_height_m":{"value":100 if status!="unknown" else None,
                        "status":status,"source":source}}}]}

def test_unknown_and_system_gates_block():
    r=assess_readiness(sample())
    assert r["summary"]["blocked"]==1+len(SYSTEM_GATES)
    assert not r["summary"]["empirical_dispatch_approved"]

def test_scenario_is_screen_only_not_approved():
    r=assess_readiness(sample("scenario_assumption"))
    assert r["gates"][0]["decision"]=="screen_only"
    assert r["summary"]["blocked"]==len(SYSTEM_GATES)

def test_documented_parameter_does_not_promote_dispatch():
    keys=("source_title","source_url","source_locator","equipment_applicability","effective_year","reviewer")
    r=assess_readiness(sample("documented_plant_specific",{k:"test" for k in keys}))
    assert r["gates"][0]["decision"]=="screen_only"
    assert not r["summary"]["empirical_dispatch_approved"]

def test_incomplete_evidence_blocks():
    r=assess_readiness(sample("documented_plant_specific",{"source_title":"test"}))
    assert r["gates"][0]["decision"]=="block"

def test_empty_registry_rejected():
    with pytest.raises(ValueError,match="nonempty"):
        assess_readiness({"sites":[]})
