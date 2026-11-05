"""Compare EIA CISO region and fuel endpoints across the 2024 missing day.

This is an observation-availability audit, not imputation.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = "https://api.eia.gov/v2/electricity/rto/"


def query(key, endpoint, start, end, facets=None):
    params = [("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
              ("facets[respondent][]", "CISO"), ("start", start), ("end", end),
              ("offset", "0"), ("length", "500")]
    for name, value in (facets or {}).items():
        params.append((f"facets[{name}][]", value))
    url = ROOT + endpoint + "/data/?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "r02-gap-crosscheck/1.0"}), timeout=60) as response:
        payload = json.load(response)["response"]
    rows = payload["data"]
    if len(rows) != int(payload["total"]):
        raise ValueError("truncated cross-endpoint query")
    return rows


def summarize(rows, start, end):
    expected = set()
    from datetime import datetime, timedelta
    t = datetime.strptime(start, "%Y-%m-%dT%H")
    last = datetime.strptime(end, "%Y-%m-%dT%H")
    while t <= last:
        expected.add(t.strftime("%Y-%m-%dT%H"))
        t += timedelta(hours=1)
    periods = {r["period"] for r in rows}
    return {"rows": len(rows), "hours": len(periods),
            "missing_hours": sorted(expected - periods),
            "present_hours": sorted(periods),
            "sample": rows[:2]}


def main():
    key = os.environ["EIA_API_KEY"]
    windows = [
        ("2024_gap", "2024-11-02T08", "2024-11-03T07"),
        ("2024_before", "2024-11-02T04", "2024-11-02T07"),
        ("2024_after", "2024-11-03T08", "2024-11-03T11"),
    ]
    for label, start, end in windows:
        for endpoint, facets in [
            ("fuel-type-data", None),
            ("region-data", {"type": "D"}),
            ("region-data", {"type": "NG"}),
            ("region-data", {"type": "TI"}),
        ]:
            rows = query(key, endpoint, start, end, facets)
            print("EIA_GAP_CROSSCHECK=" + json.dumps({
                "window": label, "endpoint": endpoint,
                "type": facets.get("type") if facets else "fuel",
                **summarize(rows, start, end)}, sort_keys=True))


if __name__ == "__main__":
    main()
