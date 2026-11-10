"""Regression tests for conservative EIA cross-endpoint diagnostics."""
import pytest

from multiyear_energy_validation.eia_cross_endpoint_audit import reconcile_fuel_and_region


def test_known_anomaly_preserves_signed_fuels():
    periods = ["2025-07-31T19", "2025-07-31T20", "2025-07-31T21",
               "2025-07-31T22", "2025-07-31T23"]
    ng = [29677, 29776, 27732, 30783, 31641]
    totals = [29677, 29775, 30003, 30783, 31642]
    region = [{"period": p, "value": v} for p, v in zip(periods, ng)]
    fuel = [
        row
        for p, total in zip(periods, totals)
        for row in (
            {"period": p, "fueltype": "OTH", "value": -10},
            {"period": p, "fueltype": "OTHER", "value": total + 10},
        )
    ]
    result = reconcile_fuel_and_region(region, fuel)
    assert [int(r["fuel_minus_region_mwh"]) for r in result] == [0, -1, 2271, 0, 1]
    assert result[2]["fuel_values_mwh"]["OTH"] == "-10"
    assert all(not r["source_corrected"] and not r["empirical_dispatch_approved"] for r in result)


def test_duplicate_region_period_fails_closed():
    with pytest.raises(ValueError, match="Duplicate region"):
        reconcile_fuel_and_region(
            [{"period": "T21", "value": 1}, {"period": "T21", "value": 2}],
            [{"period": "T21", "fueltype": "NG", "value": 1}],
        )


def test_missing_fuel_period_fails_closed():
    with pytest.raises(ValueError, match="coverage mismatch"):
        reconcile_fuel_and_region(
            [{"period": "T20", "value": 1}, {"period": "T21", "value": 2}],
            [{"period": "T20", "fueltype": "NG", "value": 1}],
        )


def test_missing_fuel_category_fails_closed():
    with pytest.raises(ValueError, match="categories differ"):
        reconcile_fuel_and_region(
            [{"period": "T20", "value": 1}, {"period": "T21", "value": 2}],
            [{"period": "T20", "fueltype": "NG", "value": 1},
             {"period": "T20", "fueltype": "OTH", "value": -1},
             {"period": "T21", "fueltype": "NG", "value": 2}],
        )


def test_nonfinite_value_fails_closed():
    with pytest.raises(ValueError, match="finite"):
        reconcile_fuel_and_region(
            [{"period": "T21", "value": "NaN"}],
            [{"period": "T21", "fueltype": "NG", "value": 1}],
        )
