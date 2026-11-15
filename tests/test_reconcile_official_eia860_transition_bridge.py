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

def test_cli_exports_reconcilable_generator_rows(tmp_path):
    import json
    import subprocess
    import sys
    write_year(tmp_path, 2024, [
        ("1", "a", "OP", 100), ("2", "b", "OP", 20),
        ("3", "c", "OA", 30), ("4", "d", "OP", 10)])
    write_year(tmp_path, 2025, [
        ("1", "a", "OP", 105), ("3", "c", "OP", 30),
        ("4", "d", "SB", 10), ("6", "f", "OP", 40)])
    output = tmp_path / "independent-transition-bridge.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--extract-dir", str(tmp_path),
         "--output", str(output)], capture_output=True, text=True)
    assert result.returncode != 0  # synthetic data must fail pinned benchmark
    assert output.is_file(), (
        f"Bridge CLI did not write JSON. exit={result.returncode}\\n"
        f"stdout={result.stdout}\\nstderr={result.stderr}")
    report = json.loads(output.read_text())
    assert report["row_level_reconciled"] is True
    assert report["row_level_rows"] == 5
    with (tmp_path / report["row_level_artifact"]).open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == report["row_level_rows"]
    assert sum(float(row["delta_mw"]) for row in rows) == 45.0
    assert all(abs(float(row["op_mw_2025"]) - float(row["op_mw_2024"]) - float(row["delta_mw"])) < 1e-6 for row in rows)
    transitions = [row for row in rows if row["component"] == "status_transitions"]
    assert {(row["status_2024"], row["status_2025"], float(row["delta_mw"])) for row in transitions} == {("OA", "OP", 30.0), ("OP", "SB", -10.0)}

def test_blank_identity_and_status_rejected(tmp_path):
    import pytest
    for bad_row, expected in [
        (("", "a", "OP", 10), "Missing generator identity"),
        (("1", "", "OP", 10), "Missing generator identity"),
        (("1", "a", "", 10), "Missing generator status"),
    ]:
        write_year(tmp_path, 2024, [bad_row])
        write_year(tmp_path, 2025, [("1", "a", "OP", 11)])
        with pytest.raises(ValueError, match=expected):
            bridge.decompose(tmp_path)

def test_proposed_and_retired_sheet_rows_do_not_change_operable_bridge(tmp_path):
    write_year(tmp_path, 2024, [("1", "a", "OP", 100)])
    write_year(tmp_path, 2025, [("1", "a", "OP", 100), ("2", "b", "OP", 40)])
    baseline, _ = bridge.decompose(tmp_path)
    for year, extra in [(2024, ("3", "c", "V", 4000, "Proposed")),
                        (2025, ("3", "c", "OP", 4000, "Retired and Canceled"))]:
        with (tmp_path / f"eia860_ciso_generators_{year}.csv").open("a", newline="") as stream:
            csv.writer(stream).writerow([year, extra[0], extra[1], extra[2], extra[3], "CISO", extra[4]])
    report, _ = bridge.decompose(tmp_path)
    assert report["components_mw"] == baseline["components_mw"]
    assert report["components_mw"]["new_to_inventory"] == 40
