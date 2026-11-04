from multiyear_energy_validation.ramp_source_audit import audit_raw_hour


def test_raw_hour_audit_matches_hour_ending_record():
    rows = [{"period": "2025-07-31T21", "respondent": "CISO",
             "type": "D", "value": "11819", "value-units": "megawatthours"}]
    report = audit_raw_hour(rows, hour_start_utc="2025-07-31T20:00:00+00:00",
                            observed_mw=11819)
    assert report["matching_raw_row_count"] == 1
    assert report["expected_raw_period_hour_ending"] == "2025-07-31T21"
    assert report["source_value_matches_normalized"] is True
    assert report["source_is_independently_verified"] is False


def test_raw_hour_audit_flags_duplicate_source_rows():
    row = {"period": "2025-07-31T21", "respondent": "CISO",
           "type": "D", "value": "11819", "value-units": "megawatthours"}
    report = audit_raw_hour([row, row], hour_start_utc="2025-07-31T20:00:00+00:00",
                            observed_mw=11819)
    assert report["matching_raw_row_count"] == 2
    assert report["source_value_matches_normalized"] is False
