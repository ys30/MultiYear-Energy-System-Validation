"""Fail-closed bridge from independently audited EIA-930 coverage to paper evidence.

Does not download EIA-930 or invent a coverage report.
"""
import calendar

def audit_eia930_coverage_reports(reports):
    if not isinstance(reports,dict) or set(reports)!={2024,2025}:
        raise ValueError("two independently audited years 2024 and 2025 required")
    rows=[]
    for year in (2024,2025):
        item=reports[year]
        expected=(366 if calendar.isleap(year) else 365)*24
        if item.get("year")!=year or item.get("expected_hours")!=expected:
            raise ValueError("incorrect year or calendar-hour denominator")
        valid=item.get("valid_hours")
        missing=item.get("missing_hours")
        unique=item.get("unique_hours")
        if any(type(x) is not int or x<0 for x in (valid,missing,unique)):
            raise ValueError("invalid hour counts")
        if unique+missing!=expected or valid>unique:
            raise ValueError("inconsistent coverage counts")
        if any(item.get(k)!=0 for k in ("duplicate_rows","invalid_timestamps","outside_year","invalid_values")):
            raise ValueError("coverage quality flags require separate resolution")
        if valid!=expected or not item.get("complete"):
            raise ValueError("incomplete demand coverage cannot be called complete")
        rows.append({"year":year,"expected_hours":expected,"valid_demand_hours":valid,
                     "demand_coverage_fraction":valid/expected})
    return {"source":"independently supplied EIA-930 demand coverage audits",
            "demand_coverage":rows,
            "fuel_series_completeness_not_inferred":True,
            "anomaly_free_not_inferred":True,
            "empirical_dispatch_approved":False}
