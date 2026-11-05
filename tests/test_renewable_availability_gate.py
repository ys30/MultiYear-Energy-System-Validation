from multiyear_energy_validation.renewable_availability_gate import (
    assess_availability_candidate, assess_hourly_availability,
)


def sample(period, tech, available=50, source_variable="weather_model_potential"):
    return {
        "period_utc": period, "technology": tech, "capacity_mw": 100,
        "available_mw": available, "source": "independent-model",
        "source_variable": source_variable, "time_basis": "UTC hour",
        "capacity_basis": "installed operational MW", "capacity_source": "EIA-860",
        "method": "documented physical model",
    }


def test_generation_proxy_is_rejected():
    result = assess_availability_candidate(
        sample("2025-01-01T00", "solar", source_variable="observed_generation"))
    assert not result["accepted"]
    assert "observed_generation_is_not_availability" in result["reasons"]


def test_capacity_bound_and_pmax():
    result = assess_availability_candidate(sample("2025-01-01T00", "wind", available=125))
    assert not result["accepted"]
    assert "availability_outside_capacity" in result["reasons"]
    valid = assess_availability_candidate(sample("2025-01-01T00", "wind"))
    assert valid["accepted"]
    assert valid["p_max_pu"] == 0.5


def test_complete_hourly_coverage_required():
    periods = ["2025-01-01T00", "2025-01-01T01"]
    rows = [sample(p, tech) for p in periods for tech in ("solar", "wind")]
    assert assess_hourly_availability(rows, periods)["accepted"]
    assert not assess_hourly_availability(rows[:-1], periods)["accepted"]


def test_duplicate_rejected():
    periods = ["2025-01-01T00"]
    rows = [sample(periods[0], "solar"), sample(periods[0], "solar"),
            sample(periods[0], "wind")]
    result = assess_hourly_availability(rows, periods)
    assert not result["accepted"]
