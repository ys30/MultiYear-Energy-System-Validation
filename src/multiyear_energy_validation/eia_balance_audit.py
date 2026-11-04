"""EIA-930 component consistency: diagnostic residuals, not a correction.

Values are provider hourly MWh, not independently measured instantaneous MW.
"""
import json
from collections import defaultdict

def audit_balance(component_reports):
    by_period = defaultdict(dict)
    for report in component_reports:
        kind = report["type"]
        if kind not in ("D", "NG", "TI"):
            raise ValueError("unexpected type")
        for row in report["rows"]:
            if row["type"] != kind or row["respondent"] != "CISO":
                raise ValueError("component mismatch")
            if row["value-units"] != "megawatthours":
                raise ValueError("unit mismatch")
            period = row["period"]
            if kind in by_period[period]:
                raise ValueError("duplicate period and type")
            by_period[period][kind] = float(row["value"])
    result = []
    for period, items in sorted(by_period.items()):
        if set(items) != {"D", "NG", "TI"}:
            raise ValueError("incomplete component triplet")
        d, ng, ti = (items[k] for k in ("D", "NG", "TI"))
        result.append({
            "period": period,
            "demand_mwh": d,
            "net_generation_mwh": ng,
            "total_interchange_mwh": ti,
            "residual_d_minus_ng_plus_ti_mwh": d - ng + ti,
            "alternative_residual_d_minus_ng_minus_ti_mwh": d - ng - ti,
            "note": "diagnostic_only_not_an_authoritative_corrected_demand",
        })
    return result
