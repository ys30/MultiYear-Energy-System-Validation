import pytest
from multiyear_energy_validation.paper_evidence_manifest import build_manifest
from multiyear_energy_validation.wind_svg_numeric_audit import KEY
from multiyear_energy_validation.empirical_dispatch_readiness import SYSTEM_GATES

def fixtures():
    reg={"sites":[{"plant_id":"solar1","technology":"solar","engineering_parameters":{"tilt":{"status":"unknown"}}},
                  {"plant_id":"wind1","technology":"wind","engineering_parameters":{"hub":{"status":"unknown"}}}]}
    gates=[{"scope":"plant","plant_id":str(s["plant_id"]),
            "technology":s["technology"],"parameter":p,"decision":"block"}
           for s in reg["sites"] for p in s["engineering_parameters"]]
    gates += [{"scope":"system","parameter":name,"decision":"block"}
              for name,_,_ in SYSTEM_GATES]
    ready={"gates":gates,"summary":{"plant_count":2,"total_gates":7,
                      "decision_counts":{"block":7,"screen_only":0,"not_applicable":0},
                      "empirical_dispatch_approved":False}}
    ids=("57484","57514","7526")
    comp={"sites":[{"plant_id":pid,"metrics":{KEY:{"2024":0.5,"2025":0.6}}} for pid in ids]}
    matched={"sites":[{"plant_id":pid,"matched_month_year_difference_pearson_r":0.7,
                       "matched_month_leave_one_out_min_r":0.6,
                       "matched_month_leave_one_out_max_r":0.8} for pid in ids]}
    audit={"numeric_checks":21,"reconciled":True}
    return reg,ready,comp,matched,audit

def test_manifest_counts_and_cohort():
    r=build_manifest(*fixtures())
    assert r["pilot"]["engineering_parameter_slots"]==2
    assert len(r["wind_diagnostics"])==3
    assert not r["readiness"]["empirical_dispatch_approved"]

def test_reject_inconsistent_gate_count():
    args=list(fixtures())
    args[1]["summary"]["total_gates"]=6
    with pytest.raises(ValueError,match="gate count"):
        build_manifest(*args)

def test_reject_unreconciled_svg():
    args=list(fixtures())
    args[4]["reconciled"]=False
    with pytest.raises(ValueError,match="reconciliation"):
        build_manifest(*args)

def test_reject_approved_dispatch():
    args=list(fixtures())
    args[1]["summary"]["empirical_dispatch_approved"]=True
    with pytest.raises(ValueError,match="dispatch approval"):
        build_manifest(*args)


def test_reject_duplicate_gate_identity():
    args=list(fixtures())
    args[1]["gates"][0]=dict(args[1]["gates"][1])
    with pytest.raises(ValueError,match="gate identities"):
        build_manifest(*args)

def test_reject_out_of_range_correlation():
    args=list(fixtures())
    args[2]["sites"][0]["metrics"][KEY]["2025"]=1.2
    with pytest.raises(ValueError,match="invalid within-year correlation"):
        build_manifest(*args)
