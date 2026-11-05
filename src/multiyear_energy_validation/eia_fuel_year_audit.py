"""Bounded EIA-930 CISO fuel-type full-year candidate audit.

2024 and 2025 are checked separately. No data is approved for dispatch.
"""
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"


def fetch_year(key, year):
    rows = []
    offset = 0
    while True:
        params = [
            ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
            ("facets[respondent][]", "CISO"),
            ("start", f"{year}-01-01T00"), ("end", f"{year}-12-31T23"),
            ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
            ("offset", str(offset)), ("length", "5000"),
        ]
        url = BASE + "?" + urlencode(params)
        with urlopen(Request(url, headers={"User-Agent": "research-year-audit/1.0"}), timeout=90) as response:
            data = json.load(response).get("response", {})
        total = int(data.get("total", -1))
        batch = data.get("data", [])
        if total < 0 or total > 100000 or not isinstance(batch, list):
            raise ValueError("invalid API response or excessive total")
        if not batch and offset < total:
            raise ValueError("unexpected empty page")
        rows.extend(batch)
        offset += len(batch)
        if offset >= total:
            if len(rows) != total:
                raise ValueError("pagination mismatch")
            return rows


def audit_year(rows, year):
    expected_hours = 8784 if year % 4 == 0 else 8760
    by_hour = defaultdict(dict)
    invalid = []
    for i, row in enumerate(rows):
        period, fuel = row.get("period"), row.get("fueltype")
        try:
            value = float(row["value"])
        except (ValueError, TypeError, KeyError):
            invalid.append(i)
            continue
        if row.get("respondent") != "CISO" or row.get("value-units") != "megawatthours":
            invalid.append(i)
        if fuel in by_hour[period]:
            invalid.append(i)
        by_hour[period][fuel] = value
    types = sorted({k for values in by_hour.values() for k in values})
    missing_fuel_counts = Counter(tuple(sorted(set(types) - set(v))) for v in by_hour.values())
    start = datetime(year, 1, 1)
    expected = {(start + timedelta(hours=i)).strftime("%Y-%m-%dT%H")
                for i in range(expected_hours)}
    missing_periods = sorted(expected - set(by_hour))
    unexpected_periods = sorted(set(by_hour) - expected)
    fuel_periods = {fuel: sorted(p for p, v in by_hour.items() if fuel in v)
                    for fuel in types}
    return {
        "year": year,
        "missing_periods": missing_periods,
        "unexpected_periods": unexpected_periods,
        "fuel_first_last_and_hours": {fuel: {"first": periods[0], "last": periods[-1],
                                             "hours": len(periods)}
                                     for fuel, periods in fuel_periods.items()},
        "coverage_pass": not missing_periods and not unexpected_periods and not invalid,
        "row_count": len(rows),
        "observed_hours": len(by_hour),
        "expected_hours": expected_hours,
        "fueltypes": types,
        "invalid_row_count": len(invalid),
        "fuel_set_patterns": [{"missing_fueltypes": list(k), "hours": v}
                              for k, v in missing_fuel_counts.items()],
        "complete_hour_count": sum(set(v) == set(types) for v in by_hour.values()),
        "candidate_not_availability": True,
        "model_input_approved": False,
    }


def main():
    key = os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("EIA_API_KEY required")
    for year in (2024, 2025):
        print("EIA_FUEL_YEAR_AUDIT=" + json.dumps(
            audit_year(fetch_year(key, year), year), sort_keys=True))


if __name__ == "__main__":
    main()
