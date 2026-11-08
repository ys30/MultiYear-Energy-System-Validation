from multiyear_energy_validation.eia923_seasonal_contrasts import seasonal_contrasts
import pytest


def fixture_report():
    return {"sites":[
        {"plant_id":"57373","summer_to_winter_generation_ratio":1.9,"july_relative_to_mean_month":1.5},
        {"plant_id":"57695","summer_to_winter_generation_ratio":1.7,"july_relative_to_mean_month":1.5},
        {"plant_id":"57484","summer_to_winter_generation_ratio":1.93,"july_relative_to_mean_month":1.33},
        {"plant_id":"57514","summer_to_winter_generation_ratio":2.34,"july_relative_to_mean_month":1.26},
        {"plant_id":"7526","summer_to_winter_generation_ratio":4.61,"july_relative_to_mean_month":2.03},
    ]}


def test_contrasts_remain_descriptive():
    out=seasonal_contrasts(fixture_report())
    assert out["target_summer_winter_exceeds_both_wind_peers"]
    assert out["target_july_relative_to_mean_exceeds_both_wind_peers"]
    assert out["target_to_peer_max_summer_winter_ratio"]==round(4.61/2.34,6)
    assert not out["weather_resource_causality_established"]
    assert not out["equipment_effect_established"]
    assert not out["empirical_dispatch_approved"]


def test_unexpected_cohort_fails():
    data=fixture_report()
    data["sites"].pop()
    with pytest.raises(ValueError,match="cohort"):
        seasonal_contrasts(data)
