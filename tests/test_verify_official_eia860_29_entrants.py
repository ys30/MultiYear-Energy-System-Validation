"""Official-extract cross-check tests; never claim operating-year verification."""
import csv
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_official_eia860_29_entrants.py"
spec = importlib.util.spec_from_file_location("entrants", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

FIELDS = ["plant_id_eia", "generator_id", "status", "nameplate_mw"]


def write_csv(path, rows, fields=FIELDS):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fixture(tmp_path):
    targets = []
    after = []
    for i in range(29):
        key = {"plant_id_eia": str(1000 + i), "generator_id": f"G{i}"}
        status = "OP" if i < 23 else ("OS" if i == 23 else "SB")
        mw = 138.1 if i == 0 else 0.0
        targets.append({**key, "reported_operating_year": "2024",
                        "status_2025": status, "op_nameplate_mw_2025": str(mw)})
        after.append({**key, "status": status, "nameplate_mw": str(mw)})
    before_path = tmp_path / "eia860_ciso_generators_2024.csv"
    after_path = tmp_path / "eia860_ciso_generators_2025.csv"
    targets_path = tmp_path / "targets.csv"
    write_csv(before_path, [])
    write_csv(after_path, after)
    write_csv(targets_path, targets, list(targets[0]))
    return targets_path, before_path, after_path


def test_valid_identity_status_capacity_without_year_claim(tmp_path):
    targets, _, _ = fixture(tmp_path)
    report = audit.verify(tmp_path, targets)
    assert report["record_count"] == 29
    assert report["op_capacity_mw"] == 138.1
    assert report["operating_year_independently_verified"] is False
    assert report["pudl_matched"] is False


def test_entrant_present_in_prior_year_rejected(tmp_path):
    targets, before, _ = fixture(tmp_path)
    write_csv(before, [{"plant_id_eia": "1000", "generator_id": "G0",
                        "status": "OP", "nameplate_mw": "138.1"}])
    with pytest.raises(ValueError, match="already in 2024"):
        audit.verify(tmp_path, targets)


def test_entrant_missing_in_current_year_rejected(tmp_path):
    targets, _, after = fixture(tmp_path)
    with after.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    write_csv(after, rows[1:])
    with pytest.raises(ValueError, match="absent from 2025"):
        audit.verify(tmp_path, targets)


def test_wrong_status_rejected(tmp_path):
    targets, _, after = fixture(tmp_path)
    with after.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[23]["status"] = "OP"
    write_csv(after, rows)
    with pytest.raises(ValueError, match="Status mismatch"):
        audit.verify(tmp_path, targets)


def test_wrong_capacity_rejected(tmp_path):
    targets, _, after = fixture(tmp_path)
    with after.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["nameplate_mw"] = "138.0"
    write_csv(after, rows)
    with pytest.raises(ValueError, match="OP capacity mismatch"):
        audit.verify(tmp_path, targets)

def test_operating_years_independently_verified_when_present(tmp_path):
    targets, _, after = fixture(tmp_path)
    with after.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row["operating_year_raw"] = "2024"
        row["operating_month_raw"] = "6"
    write_csv(after, rows, FIELDS + ["operating_year_raw", "operating_month_raw"])
    report = audit.verify(tmp_path, targets)
    assert report["operating_year_independently_verified"] is True
    assert report["operating_year_verified_count"] == 29
    assert report["operating_year_missing_count"] == 0

def test_operating_year_disagreement_fails_closed(tmp_path):
    targets, _, after = fixture(tmp_path)
    with after.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row["operating_year_raw"] = "2024"
    rows[0]["operating_year_raw"] = "2023"
    write_csv(after, rows, FIELDS + ["operating_year_raw"])
    with pytest.raises(ValueError, match="Operating year mismatch"):
        audit.verify(tmp_path, targets)
