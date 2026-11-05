"""Conservative renewable availability contract for empirical R02 PyPSA.

Observed SUN/WND generation is *not* potential generation or p_max_pu.
"""
from math import isfinite


def assess_availability_candidate(record):
    required = ("period_utc", "technology", "capacity_mw", "available_mw",
                "source", "source_variable", "time_basis", "capacity_basis")
    missing = [name for name in required if record.get(name) in (None, "")]
    if missing:
        return {"accepted": False, "reasons": ["missing:" + ",".join(missing)]}
    reasons = []
    if record["technology"] not in ("solar", "wind"):
        reasons.append("unsupported_technology")
    try:
        capacity = float(record["capacity_mw"])
        available = float(record["available_mw"])
    except (ValueError, TypeError):
        return {"accepted": False, "reasons": ["non_numeric_capacity_or_availability"]}
    if not isfinite(capacity) or not isfinite(available) or capacity <= 0:
        reasons.append("invalid_capacity_or_availability")
    elif available < 0 or available > capacity * (1 + 1e-9):
        reasons.append("availability_outside_capacity")
    source_variable = str(record["source_variable"]).lower()
    if source_variable in ("observed_generation", "generation", "eia_fuel_sun", "eia_fuel_wnd"):
        reasons.append("observed_generation_is_not_availability")
    if record.get("method") in (None, ""):
        reasons.append("missing_availability_estimation_method")
    if record.get("capacity_source") in (None, ""):
        reasons.append("missing_capacity_source")
    return {
        "accepted": not reasons,
        "reasons": reasons,
        "p_max_pu": available / capacity if capacity > 0 and isfinite(capacity) and isfinite(available) else None,
        "observed_generation_used_as_availability": False,
    }


def assess_hourly_availability(records, expected_hours):
    expected = set(expected_hours)
    if len(expected) != len(expected_hours):
        raise ValueError("duplicate expected hour")
    by_tech = {"solar": set(), "wind": set()}
    failures = []
    for index, record in enumerate(records):
        decision = assess_availability_candidate(record)
        period = record.get("period_utc")
        tech = record.get("technology")
        if period not in expected:
            failures.append({"row": index, "reasons": ["unexpected_hour"]})
        if tech in by_tech:
            if period in by_tech[tech]:
                failures.append({"row": index, "reasons": ["duplicate_technology_hour"]})
            by_tech[tech].add(period)
        if not decision["accepted"]:
            failures.append({"row": index, "reasons": decision["reasons"]})
    missing = {tech: sorted(expected - observed) for tech, observed in by_tech.items()}
    return {
        "accepted": not failures and not any(missing.values()),
        "missing_hours_by_technology": missing,
        "failed_rows": failures,
        "required_technologies": ["solar", "wind"],
        "generation_proxy_allowed": False,
    }
