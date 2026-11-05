from multiyear_energy_validation.eia_fuel_reconciliation import compare_generation_components


def test_reconciliation_preserves_cross_endpoint_discrepancy():
    rows = [
        {"period": "2025-07-31T21", "respondent": "CISO",
         "value-units": "megawatthours", "fueltype": fuel, "value": str(value)}
        for fuel, value in (("NG", 13318), ("NUC", 2271), ("SUN", 18570),
                            ("OTH", -5087), ("WND", 491), ("WAT", 420),
                            ("OIL", 20), ("COL", 0))
    ]
    result = compare_generation_components(rows, {"2025-07-31T21": 27732})
    assert result[0]["fuel_type_sum_mwh"] == 30003
    assert result[0]["fuel_minus_region_mwh"] == 2271
    assert result[0]["nuclear_mwh"] == 2271
