from multiyear_energy_validation.endpoint_eligibility import classify_endpoint_window


def test_demand_only_gap_is_not_dispatch_ready():
    hours = [f"2024-11-02T{i:02d}" for i in range(8, 24)]
    result = classify_endpoint_window(hours, {
        "D": hours, "NG": [], "TI": [], "fuel": [],
    })
    assert result["demand_descriptive_eligible"]
    assert not result["generation_interchange_empirical_eligible"]
    assert len(result["missing_hours_by_endpoint"]["NG"]) == 16
    assert not result["infer_missing_generation_from_demand"]


def test_all_observed_window_is_eligible_for_endpoint_only_check():
    hours = ["2024-11-03T08"]
    result = classify_endpoint_window(hours, {k: hours for k in ("D", "NG", "TI", "fuel")})
    assert result["generation_interchange_empirical_eligible"]


def test_missing_ti_blocks_endpoint_eligibility():
    hours = ["2024-11-02T07"]
    result = classify_endpoint_window(hours, {
        "D": hours, "NG": hours, "TI": [], "fuel": hours,
    })
    assert not result["generation_interchange_empirical_eligible"]
