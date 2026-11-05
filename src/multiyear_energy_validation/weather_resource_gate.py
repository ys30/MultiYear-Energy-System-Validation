"""Validate independently sourced hourly weather inputs for renewable potential.

Weather observations alone are not electricity availability.
"""
from math import isfinite


def assess_weather_hour(record):
    required = ("period_utc", "latitude", "longitude", "source_dataset",
                "source_version", "time_basis", "solar_irradiance_wm2",
                "wind_u100_ms", "wind_v100_ms")
    missing = [k for k in required if record.get(k) in (None, "")]
    if missing:
        return {"accepted": False, "reasons": ["missing:" + ",".join(missing)]}
    try:
        lat, lon = float(record["latitude"]), float(record["longitude"])
        ghi = float(record["solar_irradiance_wm2"])
        u, v = float(record["wind_u100_ms"]), float(record["wind_v100_ms"])
    except (ValueError, TypeError):
        return {"accepted": False, "reasons": ["non_numeric_weather"]}
    reasons = []
    if not all(isfinite(x) for x in (lat, lon, ghi, u, v)):
        reasons.append("nonfinite_weather")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        reasons.append("invalid_coordinates")
    if ghi < 0:
        reasons.append("negative_irradiance")
    if record["time_basis"] != "UTC":
        reasons.append("unverified_time_basis")
    if not record.get("irradiance_interval_definition"):
        reasons.append("missing_irradiance_interval_definition")
    if not record.get("spatial_aggregation_method"):
        reasons.append("missing_spatial_aggregation")
    return {"accepted": not reasons, "reasons": reasons,
            "wind_speed_100m_ms": (u*u+v*v)**0.5 if isfinite(u) and isfinite(v) else None,
            "renewable_potential_approved": False}


def audit_weather_coverage(records, expected_hours):
    expected = set(expected_hours)
    if len(expected) != len(expected_hours):
        raise ValueError("duplicate expected hours")
    seen = set()
    failures = []
    for index, record in enumerate(records):
        period = record.get("period_utc")
        if period in seen:
            failures.append({"row": index, "reason": "duplicate_hour"})
        seen.add(period)
        if period not in expected:
            failures.append({"row": index, "reason": "unexpected_hour"})
        result = assess_weather_hour(record)
        if not result["accepted"]:
            failures.append({"row": index, "reason": result["reasons"]})
    return {"weather_schema_accepted": not failures and seen == expected,
            "missing_hours": sorted(expected - seen),
            "failures": failures,
            "renewable_potential_approved": False}
