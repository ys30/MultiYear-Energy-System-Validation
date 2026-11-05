"""Conservative time-series fuel input eligibility checks.

UTC hourly gaps and changes in reported fuel taxonomy remain explicit.
"""
from datetime import datetime, timedelta


def assess_fuel_coverage(audit):
    year = audit["year"]
    missing = audit.get("missing_periods", [])
    unexpected = audit.get("unexpected_periods", [])
    fuel = audit.get("fuel_first_last_and_hours", {})
    expected = audit["expected_hours"]
    observed = audit["observed_hours"]
    if expected != (8784 if year % 4 == 0 else 8760):
        raise ValueError("incorrect expected UTC year length")
    if observed + len(missing) != expected or unexpected:
        raise ValueError("hour accounting inconsistent")
    geothermal = fuel.get("GEO")
    taxonomy_change = bool(geothermal and geothermal["hours"] != expected)
    return {
        "year": year,
        "utc_hour_coverage_fraction": observed / expected,
        "missing_utc_hours": missing,
        "reported_geothermal_span": geothermal,
        "taxonomy_nonstationary": taxonomy_change,
        "safe_for_unqualified_full_year_fuel_mix": not missing and not taxonomy_change,
        "missing_fuel_rows_are_not_zero_generation": True,
        "availability_derived_from_generation": False,
    }
