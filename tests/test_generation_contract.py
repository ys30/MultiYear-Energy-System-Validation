import csv

import pytest

from multiyear_energy_validation.generation_contract import REQUIRED, validate_generation_fleet


def write_fleet(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED)
        writer.writeheader()
        writer.writerows(rows)


def example(**changes):
    row = dict(
        plant_id="example-plant", generator_id="example-unit",
        technology="example-tech", capacity_mw="100",
        balancing_authority="CISO", online_date="2020-01-01",
        retirement_date="", source_name="Synthetic unit test",
        source_url="https://example.org/test-only", source_as_of="2026-01-01",
    )
    row.update(changes)
    return row


def test_explicitly_synthetic_fixture_is_not_dispatch_approved(tmp_path):
    path = tmp_path / "fleet.csv"
    write_fleet(path, [example()])
    result = validate_generation_fleet(path, year=2024)
    assert result["active_generators"] == 1
    assert result["active_nameplate_capacity_mw"] == 100
    assert result["dispatch_model_approved"] is False


@pytest.mark.parametrize("change", [
    {"balancing_authority": "OTHER"},
    {"capacity_mw": "nan"},
    {"capacity_mw": "-2"},
    {"online_date": ""},
    {"source_url": ""},
    {"retirement_date": "2019-01-01"},
])
def test_rejects_unsupported_or_invalid_fleet_rows(tmp_path, change):
    path = tmp_path / "fleet.csv"
    write_fleet(path, [example(**change)])
    with pytest.raises(ValueError):
        validate_generation_fleet(path, year=2024)


def test_rejects_duplicate_generator(tmp_path):
    path = tmp_path / "fleet.csv"
    write_fleet(path, [example(), example()])
    with pytest.raises(ValueError, match="duplicate"):
        validate_generation_fleet(path, year=2024)


def test_date_specific_active_units(tmp_path):
    path = tmp_path / "fleet.csv"
    write_fleet(path, [example(online_date="2025-01-01")])
    assert validate_generation_fleet(path, year=2024)["active_generators"] == 0


def test_midyear_commissioning_is_flagged(tmp_path):
    path = tmp_path / "fleet.csv"
    write_fleet(path, [example(online_date="2024-10-01")])
    result = validate_generation_fleet(path, year=2024)
    assert result["active_generators"] == 0
    assert result["units_with_in_year_status_changes"] == 1
    assert result["reference_snapshot_not_annual_availability"] is True


def test_midyear_retirement_is_flagged(tmp_path):
    path = tmp_path / "fleet.csv"
    write_fleet(path, [example(retirement_date="2024-09-01")])
    result = validate_generation_fleet(path, year=2024)
    assert result["active_generators"] == 1
    assert result["units_with_in_year_status_changes"] == 1
    assert result["dispatch_model_approved"] is False
