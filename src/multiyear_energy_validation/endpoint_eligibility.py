"""Explicit EIA cross-endpoint availability decisions for R02.

Demand-only periods may be used in descriptive load analysis, never treated
as fully observed generation/interchange dispatch inputs.
"""

def classify_endpoint_window(hour_labels, observations):
    hours = list(hour_labels)
    if len(hours) != len(set(hours)):
        raise ValueError("duplicate expected hour")
    required = ("D", "NG", "TI", "fuel")
    if any(key not in observations for key in required):
        raise ValueError("missing endpoint")
    observed = {key: set(observations[key]) for key in required}
    unknown = {key: sorted(values - set(hours)) for key, values in observed.items()
               if values - set(hours)}
    if unknown:
        raise ValueError(f"unexpected endpoint hours: {unknown}")
    missing = {key: sorted(set(hours) - observed[key]) for key in required}
    demand_complete = not missing["D"]
    supply_complete = not any(missing[k] for k in ("NG", "TI", "fuel"))
    return {
        "hour_count": len(hours),
        "missing_hours_by_endpoint": missing,
        "demand_descriptive_eligible": demand_complete,
        "generation_interchange_empirical_eligible": supply_complete and demand_complete,
        "infer_missing_generation_from_demand": False,
        "impute_missing_interchange": False,
    }
