"""Conservative EIA-930 cross-endpoint fuel-vs-region diagnostics.

No source value is corrected. Fuel totals are signed (including negative OTH).
All inputs must represent the same raw EIA hour-ending label and energy unit.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from decimal import Decimal, InvalidOperation
from typing import Any


def _number(value: Any) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError("Missing or invalid energy value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid energy value: {value!r}") from exc
    if not result.is_finite():
        raise ValueError("Energy must be finite")
    return result


def reconcile_fuel_and_region(
    region_rows: Iterable[Mapping[str, Any]],
    fuel_rows: Iterable[Mapping[str, Any]],
    *,
    period_key: str = "period",
    value_key: str = "value",
    fuel_key: str = "fueltype",
) -> list[dict[str, Any]]:
    """Compare NG and signed fuel totals, refusing incomplete or duplicate inputs.

    region_rows: one NG value per hour-ending period.
    fuel_rows: one value per (hour-ending period, fuel type).
    No zero-filling: incomplete fuel coverage is a separate source-quality issue.
    """
    region: dict[str, Decimal] = {}
    fuels: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for row in region_rows:
        period = str(row[period_key])
        if period in region:
            raise ValueError(f"Duplicate region period: {period}")
        region[period] = _number(row[value_key])
    for row in fuel_rows:
        period, fuel = str(row[period_key]), str(row[fuel_key])
        if not fuel or fuel == "None":
            raise ValueError("Missing fuel category")
        if fuel in fuels[period]:
            raise ValueError(f"Duplicate fuel row: {period} {fuel}")
        fuels[period][fuel] = _number(row[value_key])
    if not region or set(region) != set(fuels):
        raise ValueError("Region/fuel period coverage mismatch; refusing zero-fill")
    expected_categories = set(next(iter(fuels.values())))
    if any(set(items) != expected_categories for items in fuels.values()):
        raise ValueError("Fuel categories differ by period; cannot compare complete sums")
    return [
        {
            "period": period,
            "region_ng_mwh": str(region[period]),
            "fuel_sum_mwh": str(sum(fuels[period].values(), Decimal(0))),
            "fuel_minus_region_mwh": str(sum(fuels[period].values(), Decimal(0)) - region[period]),
            "fuel_categories": sorted(expected_categories),
            "fuel_values_mwh": {k: str(v) for k, v in sorted(fuels[period].items())},
            "source_corrected": False,
            "empirical_dispatch_approved": False,
        }
        for period in sorted(region)
    ]
