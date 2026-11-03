from multiyear_energy_validation.schema_audit import audit_candidate_values


def test_valid_raw_mwh_values():
    rows = [{"respondent": "CISO", "type": "D", "value-units": "megawatthours", "value": "123.5"}]
    result = audit_candidate_values(rows)
    assert result["all_observations_valid"]
    assert result["min_raw_mwh"] == 123.5


def test_reject_nonfinite_negative_wrong_units_and_wrong_region():
    rows = [
        {"respondent": "CISO", "type": "D", "value-units": "megawatthours", "value": "nan"},
        {"respondent": "CISO", "type": "D", "value-units": "megawatthours", "value": "-1"},
        {"respondent": "CISO", "type": "D", "value-units": "MW", "value": "12"},
        {"respondent": "OTHER", "type": "D", "value-units": "megawatthours", "value": "12"},
    ]
    result = audit_candidate_values(rows)
    assert result["invalid_observation_count"] == 4
    assert not result["all_observations_valid"]
