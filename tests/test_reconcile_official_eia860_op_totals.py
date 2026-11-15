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

def test_status_denominator_does_not_change_op_capacity_gate(tmp_path):
    for year in (2024, 2025):
        rows = sample_rows(year)
        # Reclassify one 30 MW OP unit as OA while preserving OP total MW.
        rows[0]["status"] = "OA"
        rows[-1]["nameplate_mw"] = str(round(float(rows[-1]["nameplate_mw"]) + 30, 1))
        write_rows(tmp_path, year, rows)
    result = check(tmp_path)
    assert result["op_delta_mw"] == 6895.8
    assert result["original_workbook_op_totals_reconciled"] is True
    for year in ("2024", "2025"):
        info = result["years"][year]
        assert info["op_count_difference"] == -1
        assert info["mw_matches_pinned"] is True
        assert info["alternative_denominator_count_matches"] == [
            {"included_statuses": ["OP", "OA"], "row_count": info["pinned_op_count"],
             "interpretation": "count_match_only_not_validated_op_definition"}]
        assert info["alternative_denominator_is_acceptance"] is False
        assert info["operable_sheet_count_matches_pinned"] is True

def test_broad_operable_statuses_reconcile_rows_and_op_capacity(tmp_path):
    for year in (2024, 2025):
        rows = sample_rows(year)
        for idx, status in enumerate(("OA", "OS", "SB")):
            rows[idx]["status"] = status
        rows[-1]["nameplate_mw"] = str(round(float(rows[-1]["nameplate_mw"]) + 90, 1))
        write_rows(tmp_path, year, rows)
    result = check(tmp_path)
    assert result["both_years_operable_count_matches_pinned"] is True
    assert result["original_workbook_op_totals_reconciled"] is True
    for year in ("2024", "2025"):
        info = result["years"][year]
        assert info["operable_status_set"] == ["OP", "OA", "OS", "SB"]
        assert info["operable_status_count"] == info["pinned_op_count"]
        assert info["operable_status_count_is_verified_archived_definition"] is True

def test_operable_sheet_row_count_mismatch_rejected(tmp_path):
    for year in (2024, 2025):
        rows = sample_rows(year)
        if year == 2025:
            rows[0]["status"] = "RE"
        write_rows(tmp_path, year, rows)
    report = check(tmp_path)
    assert report["original_workbook_op_totals_reconciled"] is False
    assert report["years"]["2025"]["unexpected_operable_statuses"] == ["RE"]
