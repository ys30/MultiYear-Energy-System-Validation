import csv
from datetime import datetime, timedelta, timezone

from multiyear_energy_validation.coverage import audit_coverage_csv


def make_csv(path, year, n, extra=None):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["utc", "ba", "mw"])
        for i in range(n):
            writer.writerow([(start + timedelta(hours=i)).isoformat(), "TEST", 2.0])
        for row in extra or []:
            writer.writerow(row)


def audit(path, year):
    return audit_coverage_csv(path, year=year, timestamp_column="utc",
                              demand_column="mw", region_column="ba", region="TEST")


def test_complete_leap_year(tmp_path):
    p = tmp_path / "a.csv"
    make_csv(p, 2020, 8784)
    r = audit(p, 2020)
    assert r["complete"] and r["valid_observed_mwh"] == 17568


def test_missing_and_duplicate(tmp_path):
    p = tmp_path / "a.csv"
    stamp = datetime(2021, 1, 1, tzinfo=timezone.utc).isoformat()
    make_csv(p, 2021, 8759, [[stamp, "TEST", 2]])
    r = audit(p, 2021)
    assert not r["complete"]
    assert r["missing_hours"] == 1
    assert r["duplicate_rows"] == 1


def test_bad_value_not_counted_as_valid(tmp_path):
    p = tmp_path / "a.csv"
    make_csv(p, 2021, 8759, [["2021-12-31T23:00:00+00:00", "TEST", "nan"]])
    r = audit(p, 2021)
    assert r["unique_hours"] == 8760
    assert r["valid_hours"] == 8759
    assert r["invalid_values"] == 1
    assert not r["complete"]
