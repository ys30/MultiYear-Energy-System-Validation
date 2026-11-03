"""Acceptance gate regression tests: no raw candidate is model-approved."""
from multiyear_energy_validation.schema_audit import (
    audit_period_label_grid, candidate_year_acceptance,
)


def test_complete_raw_grid_still_requires_semantic_validation():
    grid = {
        "expected_labels": 8760, "distinct_labels": 8760,
        "missing_labels": [], "unexpected_labels": [], "duplicate_labels": {},
    }
    result = candidate_year_acceptance(grid)
    assert result["candidate_label_grid_complete"] is True
    assert result["model_input_approved"] is False
    assert result["imputation_performed"] is False


def test_missing_hour_blocks_candidate_acceptance():
    grid = {
        "expected_labels": 8760, "distinct_labels": 8759,
        "missing_labels": ["2021-11-07T06"], "unexpected_labels": [],
        "duplicate_labels": {},
    }
    result = candidate_year_acceptance(grid)
    assert result["candidate_label_grid_complete"] is False
    assert result["model_input_approved"] is False
    assert result["missing_labels"] == ["2021-11-07T06"]


def test_duplicate_and_unexpected_hours_block_acceptance():
    grid = {
        "expected_labels": 8760, "distinct_labels": 8760,
        "missing_labels": [], "unexpected_labels": ["2022-01-01T00"],
        "duplicate_labels": {"2021-01-01T00": 2},
    }
    assert candidate_year_acceptance(grid)["candidate_label_grid_complete"] is False


def test_raw_grid_audit_detects_duplicates_and_missing_hours():
    rows = [
        {"period": "2021-01-01T00"},
        {"period": "2021-01-01T00"},
        {"period": "2021-01-01T01"},
    ]
    grid = audit_period_label_grid(rows, year=2021)
    assert grid["duplicate_labels"] == {"2021-01-01T00": 2}
    assert "2021-01-01T02" in grid["missing_labels"]
    assert candidate_year_acceptance(grid)["model_input_approved"] is False
