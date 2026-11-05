"""Inspect EIA-930 hourly fuel-type metadata and bounded CISO sample.

Fuel-type generation is observed output, not available generation capacity.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/"


def read_json(url):
    with urlopen(Request(url, headers={"User-Agent": "research-input-audit/1.0"}), timeout=45) as response:
        return json.load(response)


def inspect_metadata(document):
    response = document.get("response", {})
    if not isinstance(response, dict):
        raise ValueError("unexpected metadata")
    return {
        "id": response.get("id"),
        "frequency": response.get("frequency"),
        "data": response.get("data"),
        "facets": response.get("facets"),
        "status": "candidate_schema_not_empirical_input_approval",
    }


def main():
    key = os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("EIA_API_KEY required")
    meta = inspect_metadata(read_json(BASE + "?" + urlencode({"api_key": key})))
    print("EIA_FUEL_METADATA=" + json.dumps(meta, sort_keys=True))
    params = [
        ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[respondent][]", "CISO"),
        ("start", "2025-07-31T19"), ("end", "2025-07-31T23"),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("offset", "0"), ("length", "100"),
    ]
    document = read_json(BASE + "data/?" + urlencode(params))
    result = document.get("response", {})
    rows = result.get("data", [])
    total = int(result.get("total", -1))
    if not isinstance(rows, list) or total < 0 or total > 100 or len(rows) != total:
        raise ValueError("invalid, truncated or excessive candidate response")
    if any(row.get("respondent") != "CISO" for row in rows):
        raise ValueError("unexpected respondent")
    print("EIA_FUEL_CANDIDATES=" + json.dumps({
        "total": total,
        "rows": rows,
        "status": "observed_generation_candidate_not_availability",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
