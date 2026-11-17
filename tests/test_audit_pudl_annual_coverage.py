"""Regression tests for annual PUDL coverage semantics."""
import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_pudl_annual_coverage import audit


def write_csv(path, columns, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def test_missing_generator_not_physical_absence(tmp_path):
    source = tmp_path / "annual.csv"
    targets = tmp_path / "targets.csv"
    write_csv(targets, ["plant_id_eia", "generator_id"], [[10, "A"], [20, "B"]])
    write_csv(source, ["plant_id_eia", "generator_id", "report_date"], [
        [10, "OTHER", "2023-12-31"], [30, "X", "2024-12-31"],
        [10, "A", "2025-12-31"]])
    result = audit(source, targets)
    assert result["target_exact_matches_by_year"] == {"2023": 0, "2024": 0, "2025": 1}
    assert result["target_plant_matches_by_year"]["2023"] == 1
    assert result["records"][0]["classification"] == "plant_present_generator_unmatched"
    assert all(not r["physical_absence_inferred"] for r in result["records"])
    assert result["empirical_dispatch_approved"] is False


def test_missing_entire_year_fails(tmp_path):
    source = tmp_path / "annual.csv"
    targets = tmp_path / "targets.csv"
    write_csv(targets, ["plant_id_eia", "generator_id"], [[10, "A"]])
    write_csv(source, ["plant_id_eia", "generator_id", "report_date"], [
        [10, "A", "2023-12-31"], [10, "A", "2025-12-31"]])
    with pytest.raises(ValueError, match="Entire requested years missing"):
        audit(source, targets)


def test_duplicate_source_generator_year_fails(tmp_path):
    source = tmp_path / "annual.csv"
    targets = tmp_path / "targets.csv"
    write_csv(targets, ["plant_id_eia", "generator_id"], [[10, "A"]])
    write_csv(source, ["plant_id_eia", "generator_id", "report_date"], [
        [10, "A", "2023-01-01"], [10, "A", "2023-12-31"],
        [10, "A", "2024-12-31"], [10, "A", "2025-12-31"]])
    with pytest.raises(ValueError, match="Duplicate annual generator key"):
        audit(source, targets)
