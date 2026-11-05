"""ERA5 hourly solar radiation conversion with explicit interval metadata.

ERA5 SSRD is accumulated energy in J/m2. This conversion is valid only
after upstream confirms the accumulation represents exactly one hour.
"""
from math import isfinite


def hourly_ssrd_to_mean_irradiance(ssrd_j_m2, interval_seconds, interval_verified):
    if interval_verified is not True:
        raise ValueError("ERA5 accumulation interval not verified")
    seconds = float(interval_seconds)
    energy = float(ssrd_j_m2)
    if not isfinite(seconds) or seconds != 3600:
        raise ValueError("requires verified one-hour accumulation")
    if not isfinite(energy) or energy < 0:
        raise ValueError("invalid accumulated radiation")
    return energy / seconds


def wind_speed_from_components(u100_ms, v100_ms):
    u, v = float(u100_ms), float(v100_ms)
    if not isfinite(u) or not isfinite(v):
        raise ValueError("invalid 100m wind components")
    return (u*u + v*v)**0.5
