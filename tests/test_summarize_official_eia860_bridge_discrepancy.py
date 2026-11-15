"""Regression tests for official EIA-860 status-transition diagnostics."""
import csv
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/summarize_official_eia860_bridge_discrepancy.py"
spec = importlib.util.spec_from_file_location("bridge_forensics", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIELDS = ["component", "plant_id_eia", "generator_id", "status_2024",
          "status_2025", "op_mw_2024", "op_mw_2025", "delta_mw"]

def write_rows(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def test_transition_classes_and_net_delta(tmp_path):
    path = tmp_path / "bridge.csv"
    write_rows(path, [
        dict(zip(FIELDS, ["status_transitions", "6100", "1", "OA", "OP", "0", "351", "351"])),
        dict(zip(FIELDS, ["status_transitions", "6100", "2", "OA", "OP", "0", "351", "351"])),
        dict(zip(FIELDS, ["status_transitions", "12", "3", "OP", "RE", "10", "0", "-10"])),
        dict(zip(FIELDS, ["new_to_inventory", "33", "4", "", "OP", "0", "20", "20"])),
    ])
    result = mod.summarize(path)
    assert result["row_count"] == 4
    assert result["net_delta_mw"] == 712
    assert result["fleet_validated"] is False
    breakdown = {(x["component"], x["status_2024"], x["status_2025"]): x
                 for x in result["status_transition_breakdown"]}
    assert breakdown[("status_transitions", "OA", "OP")]["delta_mw"] == 702
    assert breakdown[("status_transitions", "OA", "OP")]["generator_count"] == 2
    assert breakdown[("status_transitions", "OP", "RE")]["delta_mw"] == -10
    assert breakdown[("new_to_inventory", "<absent>", "OP")]["delta_mw"] == 20

def test_empty_rows_fail_closed(tmp_path):
    path = tmp_path / "empty.csv"
    write_rows(path, [])
    with pytest.raises(ValueError, match="Empty bridge"):
        mod.summarize(path)

def test_nonfinite_delta_rejected(tmp_path):
    path = tmp_path / "invalid.csv"
    write_rows(path, [dict(zip(FIELDS, ["status_transitions", "1", "a", "OA", "OP", "0", "0", "nan"]))])
    with pytest.raises(ValueError, match="Nonfinite"):
        mod.summarize(path)
