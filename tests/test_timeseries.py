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
