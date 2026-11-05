from multiyear_energy_validation.eia_geo_transition_audit import summarize_transition


def test_geo_missing_is_not_zero():
    rows = [
        {"period": "2025-12-16T08", "fueltype": "OTH", "value": "100",
         "respondent": "CISO", "value-units": "megawatthours"},
        {"period": "2025-12-16T09", "fueltype": "OTH", "value": "90",
         "respondent": "CISO", "value-units": "megawatthours"},
        {"period": "2025-12-16T09", "fueltype": "GEO", "value": "10",
         "respondent": "CISO", "value-units": "megawatthours"},
    ]
    summary = summarize_transition(rows)
    assert summary[0]["geo_mwh"] is None
    assert not summary[0]["geo_reported"]
    assert summary[1]["geo_mwh"] == 10
    assert summary[1]["fuel_sum_mwh"] == 100
