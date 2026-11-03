from multiyear_energy_validation.schema_audit import (
    model_year_hour_ending_window, audit_model_year_hour_ending_grid,
)


def test_model_year_query_window():
    assert model_year_hour_ending_window(2024)["start"] == "2024-01-01T01"
    assert model_year_hour_ending_window(2024)["end"] == "2025-01-01T00"


def test_leap_model_year_has_8784_hours():
    rows = [
        {"period": "2024-01-01T01"},
        {"period": "2025-01-01T00"},
    ]
    report = audit_model_year_hour_ending_grid(rows, year=2024)
    assert report["expected_labels"] == 8784
    assert report["observed_rows"] == 2
    assert report["missing_labels"]
    assert not report["unexpected_labels"]


def test_old_query_window_has_wrong_year_edges():
    rows = [{"period": "2024-01-01T00"}, {"period": "2024-12-31T23"}]
    report = audit_model_year_hour_ending_grid(rows, year=2024)
    assert "2024-01-01T00" in report["unexpected_labels"]
    assert "2025-01-01T00" in report["missing_labels"]
