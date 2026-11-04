"""Tests for non-destructive EIA component balance diagnostics."""
import pytest

from multiyear_energy_validation.eia_balance_audit import audit_balance


def reports(d=11819, ng=27732, ti=-315):
    return [
        {"type": kind, "rows": [{
            "type": kind, "respondent": "CISO",
            "period": "2025-07-31T21",
            "value": str(value), "value-units": "megawatthours",
        }]}
        for kind, value in (("D", d), ("NG", ng), ("TI", ti))
    ]


def test_two_candidate_signs_are_kept_distinct():
    result = audit_balance(reports())
    assert len(result) == 1
    assert result[0]["residual_d_minus_ng_plus_ti_mwh"] == -16228
    assert result[0]["alternative_residual_d_minus_ng_minus_ti_mwh"] == -15598
    assert result[0]["demand_mwh"] == 11819


def test_missing_component_is_rejected():
    with pytest.raises(ValueError, match="incomplete"):
        audit_balance(reports()[:2])


def test_duplicate_component_is_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        audit_balance(reports() + reports()[:1])


def test_wrong_units_are_rejected():
    data = reports()
    data[0]["rows"][0]["value-units"] = "megawatts"
    with pytest.raises(ValueError, match="unit"):
        audit_balance(data)
