from datetime import datetime, timedelta, timezone
import pytest
from multiyear_energy_validation.timeseries import validate_utc_hourly

def sample(year, mw=2.0):
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    hours = 8784 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 8760
    return [(start + timedelta(hours=i), mw) for i in range(hours)]

@pytest.mark.parametrize("year,hours", [(2020, 8784), (2021, 8760)])
def test_complete_year(year, hours):
    result = validate_utc_hourly(sample(year), year)
    assert result["hours"] == hours
    assert result["annual_mwh"] == hours * 2

def test_missing_hour():
    with pytest.raises(ValueError, match="incomplete"):
        validate_utc_hourly(sample(2021)[:-1], 2021)

def test_duplicate():
    rows = sample(2021)
    with pytest.raises(ValueError, match="duplicate"):
        validate_utc_hourly(rows + [rows[0]], 2021)

def test_negative_load():
    rows = sample(2021)
    rows[0] = (rows[0][0], -1)
    with pytest.raises(ValueError, match="nonnegative"):
        validate_utc_hourly(rows, 2021)

def test_naive_time():
    rows = sample(2021)
    rows[0] = (rows[0][0].replace(tzinfo=None), 2)
    with pytest.raises(ValueError, match="UTC"):
        validate_utc_hourly(rows, 2021)

@pytest.mark.parametrize("year,hours", [(2024, 8784), (2025, 8760)])
def test_r02a_constant_profile_diagnostics(year, hours):
    result = validate_utc_hourly(sample(year, 2.0), year)
    assert result["coverage_complete"] is True
    assert result["mean_mw"] == result["median_mw"] == 2.0
    assert result["p01_mw"] == result["p99_mw"] == 2.0
    assert result["zero_load_hours"] == 0
    assert result["max_absolute_hourly_ramp_mw"] == 0.0
    assert result["min_daily_energy_mwh"] == result["max_daily_energy_mwh"] == 48.0
    assert result["peak_timestamp_utc"] == f"{year}-01-01T00:00:00+00:00"

def test_r02a_spike_and_zero_diagnostics():
    rows = sample(2025, 10.0)
    rows[0] = (rows[0][0], 0.0)
    rows[1] = (rows[1][0], 100.0)
    result = validate_utc_hourly(rows, 2025)
    assert result["zero_load_hours"] == 1
    assert result["peak_mw"] == 100.0
    assert result["min_mw"] == 0.0
    assert result["peak_timestamp_utc"] == "2025-01-01T01:00:00+00:00"
    assert result["max_absolute_hourly_ramp_mw"] == 100.0
    assert result["min_daily_energy_mwh"] == 240.0
    assert result["max_daily_energy_mwh"] == 320.0
    assert result["max_ramp_from_utc"] == "2025-01-01T00:00:00+00:00"
    assert result["max_ramp_to_utc"] == "2025-01-01T01:00:00+00:00"
    assert result["max_ramp_signed_mw"] == 100.0
    assert [x["demand_mw"] for x in result["max_ramp_context"][:3]] == [0.0, 100.0, 10.0]


def test_r02a_isolated_trough_flag_preserves_observation():
    rows = sample(2025, 30000.0)
    rows[100] = (rows[100][0], 11819.0)
    result = validate_utc_hourly(rows, 2025)
    assert result["isolated_single_hour_flag_count"] == 1
    flag = result["isolated_single_hour_flags"][0]
    assert flag["timestamp_utc"] == rows[100][0].isoformat()
    assert flag["observed_mw"] == 11819.0
    assert flag["neighbor_mean_mw"] == 30000.0
    assert rows[100][1] == 11819.0


def test_r02a_sustained_step_is_not_isolated():
    rows = sample(2025, 30000.0)
    for i in range(100, 120):
        rows[i] = (rows[i][0], 11819.0)
    result = validate_utc_hourly(rows, 2025)
    assert result["isolated_single_hour_flag_count"] == 0
