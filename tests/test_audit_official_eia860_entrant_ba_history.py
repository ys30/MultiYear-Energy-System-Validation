"""Regression tests for reported Plant-sheet BA classification (not physical transfers)."""
import csv
import io
import sys
import zipfile
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_official_eia860_entrant_ba_history import audit


def make_archive(path, plant_rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Plant"
    ws.append(["Plant Code", "Balancing Authority Code"])
    for row in plant_rows:
        ws.append(row)
    stream = io.BytesIO()
    wb.save(stream)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("2___Plant_Y2025.xlsx", stream.getvalue())


def test_ba_categories_and_no_physical_transfer_claim(tmp_path):
    before = tmp_path / "2024.zip"
    after = tmp_path / "2025.zip"
    make_archive(before, [(100, "CISO"), (200, "OTHER"), (300, "CISO")])
    make_archive(after, [(100, "CISO"), (200, "CISO"), (300, "CISO"), (400, "CISO")])
    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["plant_id_eia", "generator_id", "reported_operating_year"])
        writer.writeheader()
        for i in range(29):
            writer.writerow({"plant_id_eia": [100, 200, 300, 400][i % 4],
                             "generator_id": str(i), "reported_operating_year": "2023"})
    result = audit(before, after, targets)
    assert result["record_count"] == 29
    assert result["unique_plant_count"] == 4
    assert result["unique_plant_classification_counts"] == {
        "ciso_both_years_generator_absent_2024": 2,
        "reported_ba_changed_to_ciso": 1,
        "not_in_2024_plant_sheet": 1,
    }
    assert result["classification_counts"] == {
        "ciso_both_years_generator_absent_2024": 15,
        "reported_ba_changed_to_ciso": 7,
        "not_in_2024_plant_sheet": 7,
    }
    assert result["physical_ba_transfer_verified"] is False
    assert result["ba_mapping_validated"] is False


def test_missing_2025_ciso_fails_closed(tmp_path):
    import pytest
    before, after = tmp_path / "a.zip", tmp_path / "b.zip"
    make_archive(before, [(100, "OTHER")])
    make_archive(after, [(100, "OTHER")])
    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["plant_id_eia", "generator_id", "reported_operating_year"])
        writer.writeheader()
        for i in range(29):
            writer.writerow({"plant_id_eia": 100, "generator_id": str(i), "reported_operating_year": 2023})
    with pytest.raises(ValueError, match="does not report CISO"):
        audit(before, after, targets)

def test_earlier_plant_history_is_separate_from_transfer_claim(tmp_path):
    from audit_official_eia860_entrant_ba_history import earlier_year_presence
    old = tmp_path / "2023.zip"
    make_archive(old, [(100, "OTHER"), (200, "CISO")])
    result = earlier_year_presence({2023: old}, {"100", "200", "300"})
    assert result["2023"]["100"] == {"in_plant_sheet": True, "reported_ba": "OTHER"}
    assert result["2023"]["200"]["reported_ba"] == "CISO"
    assert result["2023"]["300"] == {"in_plant_sheet": False, "reported_ba": ""}
    import pytest
    with pytest.raises(ValueError, match="precede 2024"):
        earlier_year_presence({2024: old}, {"100"})

def test_historical_archive_sha256_gate(tmp_path):
    import hashlib
    import pytest
    from audit_official_eia860_entrant_ba_history import validate_earlier_archive_hashes
    archive = tmp_path / "2023.zip"
    make_archive(archive, [(100, "CISO")])
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    validate_earlier_archive_hashes({2023: archive}, {2023: digest})
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        validate_earlier_archive_hashes({2023: archive}, {2023: "0" * 64})
    with pytest.raises(ValueError, match="requires a matching SHA256"):
        validate_earlier_archive_hashes({2023: archive}, {})
    with pytest.raises(ValueError, match="precede 2024"):
        validate_earlier_archive_hashes({2024: archive}, {2024: digest})

def test_earlier_summary_counts_unique_plants_not_generators(tmp_path):
    before, after, old = (tmp_path / x for x in ("2024.zip", "2025.zip", "2023.zip"))
    make_archive(before, [(100, "CISO")])
    make_archive(after, [(100, "CISO"), (200, "CISO")])
    make_archive(old, [(100, "OTHER")])
    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["plant_id_eia", "generator_id", "reported_operating_year"])
        writer.writeheader()
        for i in range(29):
            writer.writerow({"plant_id_eia": 100 if i < 20 else 200,
                             "generator_id": str(i), "reported_operating_year": 2023})
    result = audit(before, after, targets, {2023: old})
    assert result["unique_plant_count"] == 2
    assert result["earlier_to_2024_plant_classification"]["2023"] == {
        "other_BA__to__ciso_both_years_generator_absent_2024": 1,
        "absent__to__not_in_2024_plant_sheet": 1,
    }
    assert result["earlier_plant_sheet_summary"]["2023"] == {
        "unique_plants_present": 1,
        "unique_plants_absent_from_plant_sheet": 1,
        "unique_plants_reported_ciso": 0,
        "unique_plants_reported_other_ba": 1,
        "unique_plants_reported_blank_ba": 0,
    }
