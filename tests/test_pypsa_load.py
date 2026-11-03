import csv
from datetime import datetime, timedelta, timezone

import pytest

from multiyear_energy_validation.pypsa_load import build_pypsa_load_profile


def write_rows(path, year, *, missing=False, duplicate=False):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    count = 8784 if year == 2024 else 8760
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_utc", "balancing_authority", "demand_mw"])
        for i in range(count - int(missing)):
            writer.writerow([(start + timedelta(hours=i)).isoformat(), "CISO", 100.0])
        if duplicate:
            writer.writerow([start.isoformat(), "CISO", 100.0])


def test_full_leap_year_exports_ordered_profile(tmp_path):
    source = tmp_path / "normalized.csv"
    write_rows(source, 2024)
    result = build_pypsa_load_profile(source, tmp_path / "load.csv", year=2024)
    assert result["snapshots"] == 8784
    assert result["annual_observed_mwh"] == 878400
    assert result["model_simulated"] is False


@pytest.mark.parametrize("missing,duplicate", [(True, False), (False, True)])
def test_rejects_incomplete_or_duplicate_data(tmp_path, missing, duplicate):
    source = tmp_path / "normalized.csv"
    write_rows(source, 2025, missing=missing, duplicate=duplicate)
    with pytest.raises(ValueError):
        build_pypsa_load_profile(source, tmp_path / "load.csv", year=2025)
