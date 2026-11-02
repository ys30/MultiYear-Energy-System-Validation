import csv
from datetime import datetime, timedelta, timezone
import pytest
from multiyear_energy_validation.eia930 import audit_csv

def write_fixture(path, year=2021, region="TEST", missing=False):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time_utc", "balancing_authority", "demand_mw"])
        for i in range(8760 - int(missing)):
            writer.writerow([(start + timedelta(hours=i)).isoformat(), region, 100.0])

def test_valid_complete_csv(tmp_path):
    path = tmp_path / "fixture.csv"
    write_fixture(path)
    audit = audit_csv(path, year=2021, timestamp_column="time_utc", demand_column="demand_mw", region_column="balancing_authority", region="TEST")
    assert audit["annual_mwh"] == 876000
    assert audit["peak_mw"] == 100

def test_missing_hour_rejected(tmp_path):
    path = tmp_path / "fixture.csv"
    write_fixture(path, missing=True)
    with pytest.raises(ValueError, match="incomplete"):
        audit_csv(path, year=2021, timestamp_column="time_utc", demand_column="demand_mw")

def test_missing_column_rejected(tmp_path):
    path = tmp_path / "fixture.csv"
    write_fixture(path)
    with pytest.raises(ValueError, match="required columns"):
        audit_csv(path, year=2021, timestamp_column="time_utc", demand_column="wrong")

def test_region_filter_required_column(tmp_path):
    path = tmp_path / "fixture.csv"
    write_fixture(path)
    with pytest.raises(ValueError, match="region_column"):
        audit_csv(path, year=2021, timestamp_column="time_utc", demand_column="demand_mw", region="TEST")
