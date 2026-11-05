from multiyear_energy_validation.weather_resource_gate import (
    assess_weather_hour, audit_weather_coverage,
)


def example(period="2025-01-01T00"):
    return {"period_utc": period, "latitude": 36.5, "longitude": -119.5,
            "source_dataset": "ERA5", "source_version": "documented",
            "time_basis": "UTC", "solar_irradiance_wm2": 250,
            "wind_u100_ms": 3, "wind_v100_ms": 4,
            "irradiance_interval_definition": "preceding hourly energy converted to mean W/m2",
            "spatial_aggregation_method": "capacity-weighted points"}


def test_weather_schema_not_power_potential():
    result = assess_weather_hour(example())
    assert result["accepted"]
    assert result["wind_speed_100m_ms"] == 5
    assert not result["renewable_potential_approved"]


def test_missing_time_semantics_rejected():
    row = example()
    row["irradiance_interval_definition"] = ""
    assert not assess_weather_hour(row)["accepted"]


def test_hourly_weather_coverage_and_duplicate():
    hours = ["2025-01-01T00", "2025-01-01T01"]
    assert audit_weather_coverage([example(h) for h in hours], hours)["weather_schema_accepted"]
    assert not audit_weather_coverage([example(hours[0]), example(hours[0])], hours)["weather_schema_accepted"]
