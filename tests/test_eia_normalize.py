import csv
import pytest
from multiyear_energy_validation.eia_normalize import normalize_candidate_rows


def row(**overrides):
    data = {"period": "2021-01-01T01:00:00+00:00",
            "respondent": "CISO", "type": "D", "units": "megawatthours",
            "value": "120"}
    data.update(overrides)
    return data


def test_requires_confirmed_interval_end(tmp_path):
    with pytest.raises(ValueError, match="interval-end"):
        normalize_candidate_rows([row()], tmp_path / "x.csv",
                                 respondent="CISO", period_is_utc_interval_end=False, period_frequency='hourly')


def test_normalizes_hour_end_to_start(tmp_path):
    p = tmp_path / "x.csv"
    assert normalize_candidate_rows([row()], p, respondent="CISO",
                                    period_is_utc_interval_end=True, period_frequency='hourly') == 1
    with p.open() as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["time_utc"] == "2021-01-01T00:00:00+00:00"
    assert rows[0]["demand_mw"] == "120.0"


def test_rejects_unexpected_series_and_units(tmp_path):
    for data in [row(type="DF"), row(units="megawatts"), row(value="nan")]:
        with pytest.raises(ValueError):
            normalize_candidate_rows([data], tmp_path / "x.csv",
                                     respondent="CISO", period_is_utc_interval_end=True)


def test_real_api_value_units_field(tmp_path):
    actual = row()
    actual["value-units"] = actual.pop("units")
    assert normalize_candidate_rows([actual], tmp_path / "real.csv",
                                    respondent="CISO", period_is_utc_interval_end=True, period_frequency="hourly") == 1


def test_real_api_unzoned_period_requires_verified_frequency(tmp_path):
    actual = row(period="2021-01-01T00")
    actual["value-units"] = actual.pop("units")
    with pytest.raises(ValueError, match="frequency=hourly"):
        normalize_candidate_rows([actual], tmp_path / "real.csv",
                                 respondent="CISO", period_is_utc_interval_end=True)

    assert normalize_candidate_rows([actual], tmp_path / "verified.csv",
                                    respondent="CISO", period_is_utc_interval_end=True,
                                    period_frequency="hourly") == 1
