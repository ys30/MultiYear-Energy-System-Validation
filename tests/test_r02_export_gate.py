import csv
import json
import pytest
from multiyear_energy_validation.r02_export_gate import verify_export
from multiyear_energy_validation.normalized_fuel import write_normalized


def test_verified_export_is_not_dispatch_approved(tmp_path):
    path = tmp_path / "fuel.csv"
    rows = [{
        "period_utc_eia": "2025-01-01T00", "respondent": "CISO",
        "fueltype": "SUN", "observed_generation_mwh": 0,
        "observation_status": "observed", "taxonomy_boundary_flag": False,
        "availability_estimate": False,
    }]
    write_normalized(rows, path, {"year": 2025, "source_coverage_pass": True})
    result = verify_export(path, path.with_suffix(".manifest.json"))
    assert result["sha256_verified"]
    assert result["observed_records"] == 1
    assert not result["r02_dispatch_approved"]


def test_corrupted_csv_rejected(tmp_path):
    path = tmp_path / "fuel.csv"
    write_normalized([], path, {"year": 2025, "source_coverage_pass": False})
    path.write_text("corrupted")
    with pytest.raises(ValueError, match="SHA-256"):
        verify_export(path, path.with_suffix(".manifest.json"))
