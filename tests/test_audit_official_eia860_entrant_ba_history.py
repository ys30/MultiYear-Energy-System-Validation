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
