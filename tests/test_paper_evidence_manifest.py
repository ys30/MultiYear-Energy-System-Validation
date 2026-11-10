import pytest
from multiyear_energy_validation.paper_evidence_manifest import build_manifest
from multiyear_energy_validation.wind_svg_numeric_audit import KEY

def fixtures():
    reg={"sites":[{"technology":"solar","engineering_parameters":{"tilt":{"status":"unknown"}}},
                  {"technology":"wind","engineering_parameters":{"hub":{"status":"unknown"}}}]}
    ready={"summary":{"plant_count":2,"total_gates":7,
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
