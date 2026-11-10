"""Regression tests based on historical EIA fuel rows, not synthetic fuel categories."""
import json
from pathlib import Path

from multiyear_energy_validation.eia_cross_endpoint_audit import reconcile_fuel_and_region

FIXTURE = Path(__file__).parent / "fixtures" / "r02a_eia_fuel_historical_20250731.json"


def test_historical_logged_fuel_rows_and_signed_sums():
    data = json.loads(FIXTURE.read_text())
    assert data["source_run_id"] == 41960929998
    rows = data["rows"]
    assert len(rows) == 40
    periods = [f"2025-07-31T{h:02d}" for h in range(19, 24)]
    assert sorted({r["period"] for r in rows}) == periods
    categories = {"COL", "NG", "NUC", "OIL", "OTH", "SUN", "WAT", "WND"}
    for period in periods:
        hour = [r for r in rows if r["period"] == period]
        assert len(hour) == 8
        assert {r["fueltype"] for r in hour} == categories
        assert all(r["value-units"] == "megawatthours" for r in hour)

    # Historical region NG values were obtained in a separate audit.
    # This is a regression comparison, not a same-run source reconciliation.
    ng = [29677, 29776, 27732, 30783, 31641]
    region = [{"period": p, "value": v} for p, v in zip(periods, ng)]
    report = reconcile_fuel_and_region(region, rows)
    assert [int(r["fuel_sum_mwh"]) for r in report] == [
        29677, 29775, 30003, 30783, 31642
    ]
    assert [int(r["fuel_minus_region_mwh"]) for r in report] == [
        0, -1, 2271, 0, 1
    ]
    assert [int(r["fuel_values_mwh"]["OTH"]) for r in report] == [
        -6332, -5870, -5087, -3415, -2057
    ]
    assert all(r["empirical_dispatch_approved"] is False for r in report)
