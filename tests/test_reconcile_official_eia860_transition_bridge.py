"""Regression tests for the four-way original-workbook OP capacity bridge."""
import csv
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reconcile_official_eia860_transition_bridge.py"
spec = importlib.util.spec_from_file_location("bridge", SCRIPT)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

FIELDS = ["year", "plant_id_eia", "generator_id", "status", "nameplate_mw", "plant_ba", "source_sheet"]

def write_year(root, year, rows):
    with (root / f"eia860_ciso_generators_{year}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for pid, gid, status, mw in rows:
            w.writerow(dict(year=year, plant_id_eia=pid, generator_id=gid,
                            status=status, nameplate_mw=mw, plant_ba="CISO",
                            source_sheet="Operable"))

def test_four_way_bridge_and_zero_nonop(tmp_path):
    write_year(tmp_path, 2024, [
        ("1", "a", "OP", 100), ("2", "b", "OP", 20),
        ("3", "c", "OA", 30), ("4", "d", "OP", 10),
        ("5", "e", "SB", 25)])
    write_year(tmp_path, 2025, [
        ("1", "a", "OP", 105), ("3", "c", "OP", 30),
        ("4", "d", "SB", 10), ("5", "e", "SB", 25),
        ("6", "f", "OP", 40)])
    report, components = bridge.decompose(tmp_path)
    assert report["components_mw"] == {
        "new_to_inventory": 40.0, "missing_from_inventory": -20.0,
        "status_transitions": 20.0, "nameplate_revisions": 5.0,
        "net_change": 45.0}
    assert report["bridge_reconciled"] is False  # synthetic fixture must not match pinned actuals
    assert len(components["status_transitions"]) == 2

def test_duplicate_identity_rejected(tmp_path):
    write_year(tmp_path, 2024, [("1", "a", "OP", 10), ("1", "a", "OP", 10)])
    write_year(tmp_path, 2025, [("1", "a", "OP", 11)])
    import pytest
    with pytest.raises(ValueError, match="Duplicate"):
        bridge.decompose(tmp_path)

def test_negative_or_nan_capacity_rejected(tmp_path):
    import pytest
    for bad in ("-1", "nan"):
        write_year(tmp_path, 2024, [("1", "a", "OP", bad)])
        write_year(tmp_path, 2025, [("1", "a", "OP", 1)])
        with pytest.raises(ValueError, match="Invalid nameplate"):
            bridge.decompose(tmp_path)

def test_missing_op_nameplate_rejected(tmp_path):
    import pytest
    write_year(tmp_path, 2024, [("1", "a", "OP", "")])
    write_year(tmp_path, 2025, [("1", "a", "OP", 1)])
    with pytest.raises(ValueError, match="Missing OP nameplate"):
        bridge.decompose(tmp_path)
