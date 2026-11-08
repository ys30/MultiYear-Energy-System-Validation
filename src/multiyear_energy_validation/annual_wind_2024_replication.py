"""Independent-year wind resource–generation descriptive replication."""
import json
from pathlib import Path
from .annual_wind_weather_generation import audit_annual_wind
from .annual_wind_monthly_alignment import summarize
from .annual_wind_first_difference import first_difference_audit

def main():
    root=Path("outputs/spatial_weather_merged_2025")
    report=audit_annual_wind("outputs/spatial_weather_pilot_2025/manifest.json",
        root/"eia923_five_site_monthly_context_2024.json",
        root/"annual_wind_weather_generation_2024.json",year=2024)
    # 2024 leap year: existing diagnostics assume February 28 days.
    # Use the 2024 daily average net generation in an equivalent 28-day February
    # monthly total so the established 2025 diagnostics normalize correctly.
    normalized=json.loads(json.dumps(report))
    for site in normalized["sites"]:
        feb=site["months"]["february"]
        feb["observed_net_generation_mwh"]*=28/29
    level=summarize(normalized)
    diff=first_difference_audit(normalized)
    output={"year":2024,"2024_february_leap_day_adjustment":True,
        "weather_hours_per_site":8784,"level":level,"first_difference":diff,
        "2024_monthly_capacity_factor_approved":False,
        "empirical_dispatch_approved":False}
    (root/"annual_wind_2024_independent_replication.json").write_text(
        json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ANNUAL_WIND_2024_INDEPENDENT_REPLICATION="+json.dumps(output,sort_keys=True))

if __name__=="__main__":main()
