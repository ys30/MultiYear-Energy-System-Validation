"""Audit EIA-860 plant location and capacity records before weather-site mapping.

Requires a separately documented CISO membership mapping; California geography
alone must not be treated as the CAISO balancing authority.
"""
from math import isfinite


def audit_plant_capacity(records, year):
    accepted = []
    rejected = []
    seen = set()
    for index, row in enumerate(records):
        reasons = []
        plant = str(row.get("plant_id", "")).strip()
        generator = str(row.get("generator_id", "")).strip()
        key = (plant, generator)
        if not plant or not generator:
            reasons.append("missing_plant_or_generator_id")
        if key in seen:
            reasons.append("duplicate_generator")
        seen.add(key)
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            mw = float(row["capacity_mw"])
        except (KeyError, ValueError, TypeError):
            reasons.append("missing_or_invalid_coordinates_or_capacity")
            lat = lon = mw = float("nan")
        if not all(isfinite(x) for x in (lat, lon, mw)) or mw <= 0:
            reasons.append("invalid_capacity_or_location")
        if isfinite(lat) and isfinite(lon) and not (-90 <= lat <= 90 and -180 <= lon <= 180):
            reasons.append("out_of_range_coordinates")
        if row.get("technology") not in ("solar", "wind"):
            reasons.append("unsupported_technology")
        if str(row.get("report_year")) != str(year):
            reasons.append("wrong_reporting_year")
        if row.get("operating_status") != "OP":
            reasons.append("not_confirmed_operational")
        if row.get("ciso_membership_verified") is not True:
            reasons.append("ciso_membership_not_verified")
        if reasons:
            rejected.append({"row": index, "plant_id": plant, "generator_id": generator,
                             "reasons": reasons})
        else:
            accepted.append({"plant_id": plant, "generator_id": generator,
                             "latitude": lat, "longitude": lon, "capacity_mw": mw,
                             "technology": row["technology"], "year": year})
    return {
        "year": year, "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted_capacity_mw": sum(row["capacity_mw"] for row in accepted),
        "accepted": accepted, "rejected": rejected,
        "weather_capacity_mapping_approved": bool(accepted) and not rejected,
        "dispatch_approved": False,
    }
