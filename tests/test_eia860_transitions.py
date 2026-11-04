import csv

import pytest

from multiyear_energy_validation.eia860_transitions import compare


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "plant_id", "generator_id", "status_raw", "technology",
            "nameplate_capacity_mw"])
        writer.writeheader()
        writer.writerows(rows)


def row(plant, gen, status="OP", mw=100, tech="Solar Photovoltaic"):
    return dict(plant_id=plant, generator_id=gen, status_raw=status,
                technology=tech, nameplate_capacity_mw=mw)


def test_reconciles_new_missing_status_and_capacity(tmp_path):
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    write(old, [row("1", "A"), row("1", "B", mw=40),
                row("1", "C", status="OS", mw=20), row("1", "D", mw=50)])
    write(new, [row("1", "A", mw=120), row("1", "C", mw=20),
                row("1", "D", status="OS", mw=50), row("2", "E", mw=30)])
    result = compare(old, new, tmp_path / "out.json")
    assert result["classification_counts"] == {
        "missing_from_ciso_inventory": 1, "nameplate_changed": 1,
        "new_to_ciso_inventory": 1, "status_changed": 2}
    assert result["op_previous_nameplate_mw"] == 190
    assert result["op_current_nameplate_mw"] == 170
    assert result["op_delta_nameplate_mw"] == -20
    assert result["empirical_dispatch_ready"] is False
    assert result["op_delta_by_technology_mw"] == {"Solar Photovoltaic": -20.0}
    assert sum(result["op_delta_by_technology_mw"].values()) == result["op_delta_nameplate_mw"]


def test_rejects_duplicate_ids(tmp_path):
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    write(old, [row("1", "A"), row("1", "A")])
    write(new, [row("1", "A")])
    with pytest.raises(ValueError, match="duplicate"):
        compare(old, new, tmp_path / "out.json")

def test_technology_reclassification_conserves_capacity(tmp_path):
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    write(old, [row("1", "A", mw=100, tech="Solar Photovoltaic")])
    write(new, [row("1", "A", mw=100, tech="Onshore Wind Turbine")])
    result = compare(old, new, tmp_path / "out.json")
    assert result["op_delta_nameplate_mw"] == 0
    assert result["op_delta_by_technology_mw"] == {
        "Onshore Wind Turbine": 100.0, "Solar Photovoltaic": -100.0}
    assert result["classification_counts"]["technology_changed"] == 1
