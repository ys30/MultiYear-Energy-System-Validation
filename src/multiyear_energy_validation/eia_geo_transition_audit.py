"""Audit EIA CISO GEO introduction against OTH and total fuel generation.

The report detects discontinuities but does not attribute a taxonomy revision.
"""
import json
import os
from collections import defaultdict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"


def summarize_transition(rows):
    grouped = defaultdict(dict)
    for row in rows:
        if row.get("respondent") != "CISO" or row.get("value-units") != "megawatthours":
            raise ValueError("unexpected respondent or unit")
        period, fuel = row["period"], row["fueltype"]
        if fuel in grouped[period]:
            raise ValueError("duplicate period and fuel")
        grouped[period][fuel] = float(row["value"])
    result = []
    for period, fuels in sorted(grouped.items()):
        result.append({
            "period": period,
            "geo_reported": "GEO" in fuels,
            "geo_mwh": fuels.get("GEO"),
            "other_mwh": fuels.get("OTH"),
            "fuel_sum_mwh": sum(fuels.values()),
            "fuel_count": len(fuels),
        })
    return result


def main():
    key = os.environ["EIA_API_KEY"]
    params = [
        ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[respondent][]", "CISO"),
        ("start", "2025-12-15T00"), ("end", "2025-12-17T23"),
        ("offset", "0"), ("length", "1000"),
    ]
    with urlopen(Request(URL + "?" + urlencode(params),
                         headers={"User-Agent": "r02-geo-transition-audit/1.0"}), timeout=60) as response:
        response_data = json.load(response)["response"]
    rows = response_data["data"]
    if len(rows) != int(response_data["total"]):
        raise ValueError("truncated response")
    summary = summarize_transition(rows)
    for row in summary:
        if row["period"] in (
            "2025-12-16T07", "2025-12-16T08",
            "2025-12-16T09", "2025-12-16T10", "2025-12-16T11",
        ):
            print("EIA_GEO_TRANSITION=" + json.dumps(row, sort_keys=True))
    print("EIA_GEO_TRANSITION_COVERAGE=" + json.dumps({
        "hours": len(summary),
        "geo_reported_hours": sum(row["geo_reported"] for row in summary),
        "first_geo_period": next((row["period"] for row in summary if row["geo_reported"]), None),
        "interpretation": "candidate_reporting_transition_not_proven_reclassification",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
