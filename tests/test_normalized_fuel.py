from multiyear_energy_validation.normalized_fuel import (
    expected_utc_hours, normalize_fuel_records, write_normalized,
)


def test_expected_utc_leap_year():
    assert len(expected_utc_hours(2024)) == 8784
    assert len(expected_utc_hours(2025)) == 8760
    assert "2024-02-29T12" in expected_utc_hours(2024)


def test_missing_not_zero_and_negative_preserved():
    records = [
        {"respondent": "CISO", "period": "2025-12-16T08", "fueltype": "OTH",
         "value": "-368", "value-units": "megawatthours"},
        {"respondent": "CISO", "period": "2025-12-16T09", "fueltype": "GEO",
         "value": "729", "value-units": "megawatthours"},
    ]
    rows = normalize_fuel_records(records, 2025)
    assert len(rows) == 8760 * 9
    lookup = {(r["period_utc_eia"], r["fueltype"]): r for r in rows}
    assert lookup[("2025-12-16T08", "OTH")]["observed_generation_mwh"] == -368
    assert lookup[("2025-12-16T08", "GEO")]["observed_generation_mwh"] is None
    assert lookup[("2025-12-16T08", "GEO")]["taxonomy_boundary_flag"]
    assert lookup[("2025-12-16T09", "GEO")]["observed_generation_mwh"] == 729
    assert lookup[("2025-12-16T09", "GEO")]["availability_estimate"] is False


def test_duplicate_rejected():
    record = {"respondent": "CISO", "period": "2024-01-01T00",
              "fueltype": "NG", "value": "1", "value-units": "megawatthours"}
    try:
        normalize_fuel_records([record, record], 2024)
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate should be rejected")


def test_manifest_checksum(tmp_path):
    path = tmp_path / "normalized.csv"
    manifest = write_normalized([], path, {"source": "EIA-930"})
    assert manifest["row_count"] == 0
    assert len(manifest["sha256"]) == 64
    assert path.with_suffix(".manifest.json").exists()
