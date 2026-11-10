"""Merge independently generated annual EIA demand coverage exports.

Requires both real-year artifacts. Does not infer fuel coverage or source quality.
"""
import json
from pathlib import Path

def merge_demand_coverage(reports):
    if not isinstance(reports,dict) or set(reports)!={2024,2025}:
        raise ValueError("both 2024 and 2025 reports required")
    years=[]
    for year in (2024,2025):
        r=reports[year]
        expected=8784 if year==2024 else 8760
        if (r.get("year")!=year or r.get("expected_hours")!=expected
                or r.get("valid_demand_hours")!=expected
                or r.get("demand_coverage_fraction")!=1.0):
            raise ValueError("year coverage not fully verified")
        if (r.get("anomaly_free_not_inferred") is not True
                or r.get("fuel_series_completeness_not_inferred") is not True
                or r.get("empirical_dispatch_approved") is not False):
            raise ValueError("source caveats missing or dispatch approval unsafe")
        years.append(r)
    return {"schema_version":"1.0","series":"EIA-930 CISO observed hourly demand",
            "years":years,"expected_hours_total":17544,
            "valid_demand_hours_total":sum(r["valid_demand_hours"] for r in years),
            "fuel_coverage_not_inferred":True,
            "anomaly_free_not_inferred":True,
            "empirical_dispatch_approved":False}

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--year-2024",type=Path,required=True)
    parser.add_argument("--year-2025",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    merged=merge_demand_coverage({
        2024:json.loads(args.year_2024.read_text(encoding="utf-8")),
        2025:json.loads(args.year_2025.read_text(encoding="utf-8"))})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(merged,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PAPER_DEMAND_TWO_YEAR="+json.dumps({
        "years":[r["year"] for r in merged["years"]],
        "valid_hours":merged["valid_demand_hours_total"],
        "empirical_dispatch_approved":False},sort_keys=True))

if __name__=="__main__":main()
