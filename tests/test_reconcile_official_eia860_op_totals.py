"""Regression tests for independent annual OP reconciliation."""
import csv
import pytest
from scripts.reconcile_official_eia860_op_totals import check

FIELDS = ["plant_id_eia", "generator_id", "status", "nameplate_mw"]

def write_rows(directory, year, rows):
    with (directory / f"eia860_ciso_generators_{year}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def sample_rows(year):
    count, total = ((2645, 85634.2) if year == 2024 else (2786, 92530.0))
    # A constructed fixture with exact expected total and count; not EIA data.
    normal = 30.0
    last = round(total - normal * (count - 1), 1)
    return [{"plant_id_eia": str(i + 10000), "generator_id": "A",
             "status": "OP", "nameplate_mw": str(normal if i < count - 1 else last)}
            for i in range(count)]

def test_matching_inventory_passes(tmp_path):
    for year in (2024, 2025):
        write_rows(tmp_path, year, sample_rows(year))
    result = check(tmp_path)
    assert result["original_workbook_op_totals_reconciled"] is True
    assert result["op_delta_mw"] == 6895.8
    assert result["empirical_dispatch_approved"] is False

def test_capacity_drift_fails(tmp_path):
    for year in (2024, 2025):
        rows = sample_rows(year)
        if year == 2025:
            rows[-1]["nameplate_mw"] = str(float(rows[-1]["nameplate_mw"]) + 1)
        write_rows(tmp_path, year, rows)
    with pytest.raises(ValueError, match="does not match pinned"):
        check(tmp_path)

def test_duplicate_identity_fails(tmp_path):
    for year in (2024, 2025):
        rows = sample_rows(year)
        if year == 2025:
            rows[1]["plant_id_eia"] = rows[0]["plant_id_eia"]
        write_rows(tmp_path, year, rows)
    with pytest.raises(ValueError, match="duplicate generator identity"):
        check(tmp_path)
