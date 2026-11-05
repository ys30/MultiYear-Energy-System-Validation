import pytest
from multiyear_energy_validation.era5_units import (
    hourly_ssrd_to_mean_irradiance, wind_speed_from_components,
)


def test_hourly_ssrd_joules_to_watts():
    assert hourly_ssrd_to_mean_irradiance(3600000, 3600, True) == 1000


def test_unverified_interval_rejected():
    with pytest.raises(ValueError, match="not verified"):
        hourly_ssrd_to_mean_irradiance(3600000, 3600, False)


def test_nonhourly_interval_rejected():
    with pytest.raises(ValueError, match="one-hour"):
        hourly_ssrd_to_mean_irradiance(3600000, 10800, True)


def test_negative_energy_rejected():
    with pytest.raises(ValueError, match="radiation"):
        hourly_ssrd_to_mean_irradiance(-1, 3600, True)


def test_wind_components():
    assert wind_speed_from_components(3, 4) == 5
