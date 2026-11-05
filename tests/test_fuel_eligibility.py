from multiyear_energy_validation.fuel_eligibility import assess_fuel_coverage


def test_2024_missing_24_hours_blocks_unqualified_full_year_mix():
    result = assess_fuel_coverage({
        "year": 2024, "expected_hours": 8784, "observed_hours": 8760,
        "missing_periods": [f"missing-{i}" for i in range(24)],
        "unexpected_periods": [], "fuel_first_last_and_hours": {},
    })
    assert not result["safe_for_unqualified_full_year_fuel_mix"]
    assert result["utc_hour_coverage_fraction"] == 8760 / 8784


def test_2025_geothermal_taxonomy_change_blocks_unqualified_mix():
    result = assess_fuel_coverage({
        "year": 2025, "expected_hours": 8760, "observed_hours": 8760,
        "missing_periods": [], "unexpected_periods": [],
        "fuel_first_last_and_hours": {
            "GEO": {"first": "2025-12-16T09", "last": "2025-12-31T23", "hours": 375}
        },
    })
    assert result["taxonomy_nonstationary"]
    assert not result["safe_for_unqualified_full_year_fuel_mix"]
    assert result["missing_fuel_rows_are_not_zero_generation"]
