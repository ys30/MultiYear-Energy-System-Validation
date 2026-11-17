"""Tests for the 29-generator x 3-year evidence matrix."""
import csv
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_pudl_annual_eia860_evidence_matrix import build_matrix


def fixtures(tmp_path):
    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["plant_id_eia", "generator_id", "reported_operating_year", "status_2025", "op_nameplate_mw_2025"])
        for i in range(29):
            w.writerow([100 + i, "G", 2024, "OP", 1])
    rows = []
    for i in range(29):
        for year in (2023, 2024, 2025):
            rows.append({"plant_id_eia": 100 + i, "generator_id": "G",
                         "year": year, "classification": "plant_unmatched",
                         "exact_generator_record": False})
    receipt = {"input_kind": "PUDL_annual_generators", "empirical_dispatch_approved": False,
               "source_sha256": "a" * 64, "targets_sha256": hashlib.sha256(targets.read_bytes()).hexdigest(), "records": rows}
    return targets, receipt


def test_matrix_is_descriptive(tmp_path):
    targets, receipt = fixtures(tmp_path)
    result = build_matrix(receipt, targets)
    assert result["target_year_rows"] == 87
    assert result["physical_commissioning_verified"] is False
    assert result["empirical_dispatch_approved"] is False
    assert result["rows"][0]["historical_year_before_reported_operation"] is True


def test_missing_target_year_rejected(tmp_path):
    targets, receipt = fixtures(tmp_path)
    receipt["records"].pop()
    with pytest.raises(ValueError, match="Expected 87"):
        build_matrix(receipt, targets)


def test_duplicate_target_year_rejected(tmp_path):
    targets, receipt = fixtures(tmp_path)
    receipt["records"][1] = dict(receipt["records"][0])
    with pytest.raises(ValueError, match="duplicate"):
        build_matrix(receipt, targets)


def test_tampered_target_file_rejected(tmp_path):
    targets, receipt = fixtures(tmp_path)
    with targets.open("a") as f:
        f.write("\\n")
    with pytest.raises(ValueError, match="SHA256"):
        build_matrix(receipt, targets)
