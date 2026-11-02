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
                                 respondent="CISO", period_is_utc_interval_end=False)


def test_normalizes_hour_end_to_start(tmp_path):
    p = tmp_path / "x.csv"
    assert normalize_candidate_rows([row()], p, respondent="CISO",
                                    period_is_utc_interval_end=True) == 1
    with p.open() as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["time_utc"] == "2021-01-01T00:00:00+00:00"
    assert rows[0]["demand_mw"] == "120.0"


def test_rejects_unexpected_series_and_units(tmp_path):
    for data in [row(type="DF"), row(units="megawatts"), row(value="nan")]:
        with pytest.raises(ValueError):
            normalize_candidate_rows([data], tmp_path / "x.csv",
                                     respondent="CISO", period_is_utc_interval_end=True)
