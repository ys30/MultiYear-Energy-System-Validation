"""Candidate EIA-930 component check; do not infer sign conventions from codes."""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.eia.gov/v2/electricity/rto/region-data/data/"


def fetch_component(*, api_key, kind, start="2025-07-31T19", end="2025-07-31T23"):
    if kind not in ("D", "NG", "TI"):
        raise ValueError("unsupported component")
    params = [
        ("api_key", api_key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[respondent][]", "CISO"), ("facets[type][]", kind),
        ("start", start), ("end", end),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("offset", "0"), ("length", "100"),
    ]
    url = BASE + "?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "research-audit/1.0"}), timeout=40) as response:
        body = json.load(response)
    result = body.get("response", {})
    rows = result.get("data", [])
    if not isinstance(rows, list):
        raise ValueError("unexpected response")
    return {"type": kind, "total": result.get("total"), "rows": [
        {key: row.get(key) for key in ("period", "type", "respondent", "value", "value-units")}
        for row in rows
    ]}


def main():
    key = os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("EIA_API_KEY required")
    report = [fetch_component(api_key=key, kind=kind) for kind in ("D", "NG", "TI")]
    print("EIA_COMPONENT_CANDIDATES=" + json.dumps(report, sort_keys=True))
    print("EIA_COMPONENT_INTERPRETATION=unverified_sign_and_scope")


if __name__ == "__main__":
    main()
