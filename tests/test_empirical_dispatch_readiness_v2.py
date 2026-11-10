import pytest
from multiyear_energy_validation.empirical_dispatch_readiness_v2 import assess_v2, SYSTEM_GATES

def registry():
    return {"sites":[{"plant_id":1,"technology":"wind","engineering_parameters":{
        "hub_height_m":{"status":"unknown","value":None}}}]}

def test_baseline_counts():
    result=assess_v2(registry())
    assert result["summary"]["decision_counts"]["block"]==1+len(SYSTEM_GATES)
    assert not result["summary"]["empirical_dispatch_approved"]

def test_explicit_nonapplicability():
    name=SYSTEM_GATES[2][0]
    result=assess_v2(registry(),{name:{"state":"not_applicable"}},{name:False,name+"_justification":{"rationale":"scope excludes storage","reviewer":"test reviewer"}})
    assert result["summary"]["decision_counts"]["not_applicable"]==1
    assert result["summary"]["decision_counts"]["block"]==len(SYSTEM_GATES)
    assert not result["summary"]["empirical_dispatch_approved"]

def test_nonapplicable_requires_scope():
    name=SYSTEM_GATES[2][0]
    with pytest.raises(ValueError,match="applicable requirement"):
        assess_v2(registry(),{name:{"state":"not_applicable"}})

def test_scope_requires_explicit_nonapplicability():
    name=SYSTEM_GATES[2][0]
    with pytest.raises(ValueError,match="explicit not_applicable"):
        assess_v2(registry(),scope={name:False})

def test_unsubstantiated_validated_claim_rejected():
    name=SYSTEM_GATES[0][0]
    with pytest.raises(ValueError,match="traceable evidence"):
        assess_v2(registry(),{name:{"state":"validated"}})

def test_documented_claim_still_no_automatic_dispatch_approval():
    name=SYSTEM_GATES[0][0]
    keys=("source_title","source_url","source_locator","equipment_applicability","effective_year","reviewer")
    ev={k:"reviewed" for k in keys}
    ev["source_url"]="https://example.org/source"
    r=assess_v2(registry(),{name:{"state":"validated","evidence":ev}})
    assert r["summary"]["decision_counts"]["screen_only"]==1
    assert not r["summary"]["empirical_dispatch_approved"]

def test_invalid_state_rejected():
    name=SYSTEM_GATES[0][0]
    with pytest.raises(ValueError,match="invalid state"):
        assess_v2(registry(),{name:{"state":"observed"}})


def test_nonapplicability_without_review_is_rejected():
    name=SYSTEM_GATES[2][0]
    with pytest.raises(ValueError,match="rationale and reviewer"):
        assess_v2(registry(),{name:{"state":"not_applicable"}},{name:False})
