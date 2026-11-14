"""Helms official-extract audit regression fixtures."""
import csv
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_official_eia860_helms.py"
spec = importlib.util.spec_from_file_location("helms_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def write(root, year, status, missing=None):
    with (root / f"eia860_ciso_generators_{year}.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["plant_id_eia", "generator_id", "status", "nameplate_mw"])
        writer.writeheader()
        for gid in ("1", "2", "3"):
            if gid != missing:
                writer.writerow({"plant_id_eia": "6100", "generator_id": gid,
                                 "status": status, "nameplate_mw": "351"})


def test_helms_oa_op(tmp_path):
    write(tmp_path, 2024, "OA")
    write(tmp_path, 2025, "OP")
    report = audit.verify(tmp_path)
    assert report["helms_transition_reconciled"] is True
    assert report["helms_op_delta_mw"] == 1053.0
    assert report["fleet_validated"] is False


def test_missing_helms_unit_fails(tmp_path):
    write(tmp_path, 2024, "OA", missing="2")
    write(tmp_path, 2025, "OP")
    with pytest.raises(ValueError, match="missing"):
        audit.verify(tmp_path)


def test_wrong_status_fails(tmp_path):
    write(tmp_path, 2024, "OP")
    write(tmp_path, 2025, "OP")
    with pytest.raises(ValueError, match="statuses"):
        audit.verify(tmp_path)
