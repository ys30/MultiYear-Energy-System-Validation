import json

import pytest

from multiyear_energy_validation.dispatch_readiness import (
    REQUIRED_EVIDENCE,
    assess_dispatch_readiness,
    require_empirical_dispatch_ready,
)


def test_incomplete_evidence_blocks_dispatch(tmp_path):
    path = tmp_path / "audit.json"
    path.write_text(json.dumps({
        "year": 2024, "scope": "EIA-860 CISO",
        "capacity_reconciliation_passed": True,
        "dispatch_model_approved": False,
    }))
    result = assess_dispatch_readiness(path, {"hourly_load_profile": True})
    assert not result["empirical_dispatch_ready"]
    assert "storage_power_and_energy_capacity" in result["missing_evidence"]
    with pytest.raises(RuntimeError, match="empirical dispatch blocked"):
        require_empirical_dispatch_ready(path, {"hourly_load_profile": True})


def test_reject_unreconciled_fleet(tmp_path):
    path = tmp_path / "audit.json"
    path.write_text(json.dumps({"year": 2025, "scope": "test"}))
    with pytest.raises(ValueError, match="reconciliation"):
        assess_dispatch_readiness(path, {})


def test_full_explicit_evidence_is_required(tmp_path):
    path = tmp_path / "audit.json"
    path.write_text(json.dumps({
        "year": 2025, "scope": "test", "capacity_reconciliation_passed": True,
        "dispatch_model_approved": False,
    }))
    evidence = dict.fromkeys(REQUIRED_EVIDENCE, True)
    assert require_empirical_dispatch_ready(path, evidence)["empirical_dispatch_ready"]
    evidence["hourly_renewable_availability"] = "true"
    assert not assess_dispatch_readiness(path, evidence)["empirical_dispatch_ready"]
