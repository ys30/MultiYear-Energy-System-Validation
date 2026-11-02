import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone

from multiyear_energy_validation.reporting import write_coverage_report


def test_report_is_reproducible_and_records_checksum(tmp_path):
    source = tmp_path / "observations.csv"
    start = datetime(2021, 1, 1, tzinfo=timezone.utc)
    with source.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["utc", "region", "demand"])
        for hour in range(8760):
            writer.writerow([(start + timedelta(hours=hour)).isoformat(), "TEST", 10])
    report = write_coverage_report(
        source, tmp_path / "reports", year=2021,
        timestamp_column="utc", demand_column="demand",
        region_column="region", region="TEST",
        source_uri="synthetic-test-fixture",
    )
    assert report["complete"]
    assert report["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert report["data_status"] == "candidate_not_empirically_verified"
    audit = json.loads((tmp_path / "reports" / "TEST_2021_audit.json").read_text())
    assert audit["valid_observed_mwh"] == 87600
    with (tmp_path / "reports" / "TEST_2021_table1.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["missing_hours"] == "0"
