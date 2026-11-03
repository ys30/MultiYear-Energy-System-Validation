from multiyear_energy_validation.schema_audit import audit_utc_interval_hypotheses


def test_start_and_end_hypotheses_differ_at_year_boundary():
    rows = [{"period": "2024-01-01T00"}, {"period": "2024-12-31T23"}]
    report = audit_utc_interval_hypotheses(rows, year=2024)
    assert report["hypotheses"]["interval_start"]["outside_requested_year"] == 0
    assert report["hypotheses"]["interval_end"]["outside_requested_year"] == 1
    assert report["selected_hypothesis"] is None
    assert report["model_input_approved"] is False


def test_invalid_raw_period_is_flagged():
    report = audit_utc_interval_hypotheses([{"period": "bad"}], year=2025)
    assert report["malformed_period_rows"] == [0]
