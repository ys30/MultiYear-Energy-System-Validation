"""Minimal checks for physical units and annual energy accounting."""
import calendar
import math

def expected_hours(year: int) -> int:
    if not isinstance(year, int) or isinstance(year, bool) or year < 1900:
        raise ValueError("year must be an integer >= 1900")
    return (366 if calendar.isleap(year) else 365) * 24

def check_annual_energy(hourly_mw, annual_mwh: float, *, tolerance: float = 1e-6) -> None:
    """Check hourly MW observations integrated over contiguous 1-hour intervals.

    This helper assumes one observation per hourly interval, no duplicates,
    no missing intervals, and a single calendar year. Callers must independently
    validate timestamps, time zones and coverage before using it.
    """
    values = list(hourly_mw)
    if not values or not math.isfinite(float(annual_mwh)) or annual_mwh < 0:
        raise ValueError("invalid annual demand or empty hourly series")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("invalid tolerance")
    if any(not math.isfinite(float(v)) or float(v) < 0 for v in values):
        raise ValueError("hourly MW must be finite and nonnegative")
    measured_mwh = math.fsum(float(v) for v in values)
    if not math.isclose(measured_mwh, annual_mwh, rel_tol=tolerance, abs_tol=1e-6):
        raise ValueError(f"annual energy mismatch: hourly={measured_mwh}, expected={annual_mwh}")
