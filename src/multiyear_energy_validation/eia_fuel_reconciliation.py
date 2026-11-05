"""Cross-check EIA fuel-type generation sums against region-data NG.

Never infer a correction from disagreement between provider datasets.
"""


def compare_generation_components(fuel_rows, region_ng_by_period):
    grouped = {}
    for row in fuel_rows:
        if row.get("respondent") != "CISO" or row.get("value-units") != "megawatthours":
            raise ValueError("fuel row identity or units mismatch")
        period = row["period"]
        fuel = row["fueltype"]
        grouped.setdefault(period, {})
        if fuel in grouped[period]:
            raise ValueError("duplicate fuel/period")
        grouped[period][fuel] = float(row["value"])
    results = []
    for period, fuels in sorted(grouped.items()):
        if period not in region_ng_by_period:
            raise ValueError("missing region NG")
        fuel_sum = sum(fuels.values())
        region_ng = float(region_ng_by_period[period])
        results.append({
            "period": period,
            "fuel_type_sum_mwh": fuel_sum,
            "region_net_generation_mwh": region_ng,
            "fuel_minus_region_mwh": fuel_sum - region_ng,
            "nuclear_mwh": fuels.get("NUC"),
            "fuel_types": sorted(fuels),
            "classification": "provider_cross_endpoint_discrepancy_not_correction",
        })
    return results
