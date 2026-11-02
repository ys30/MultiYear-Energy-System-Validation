"""Conservative EIA API v2 client: metadata first, no timestamp reinterpretation."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.eia.gov/v2/electricity/rto/region-data/"


def build_request_url(*, api_key, respondent, start, end, offset=0, length=5000):
    """Build paginated candidate hourly demand request; validate facets via metadata."""
    if not api_key or not respondent or not start or not end:
        raise ValueError("api_key, respondent, start and end required")
    if not (0 <= offset and 1 <= length <= 5000):
        raise ValueError("invalid pagination")
    params = [
        ("api_key", api_key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[type][]", "D"), ("facets[respondent][]", respondent),
        ("start", start), ("end", end),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("offset", str(offset)), ("length", str(length)),
    ]
    return BASE + "data/?" + urlencode(params)


def fetch_json(url, *, timeout=30):
    """Fetch a single JSON response; never print or persist credential-bearing URL."""
    req = Request(url, headers={"User-Agent": "multiyear-energy-validation/0.1"})
    with urlopen(req, timeout=timeout) as response:
        result = json.load(response)
    if not isinstance(result, dict) or not isinstance(result.get("response"), dict):
        raise ValueError("unexpected EIA response")
    return result["response"]


def fetch_metadata(*, api_key):
    """Retrieve live route metadata for manual verification before data download."""
    return fetch_json(BASE + "?" + urlencode({"api_key": api_key}))


def fetch_candidate_pages(*, api_key, respondent, start, end, max_rows=20000):
    """Retrieve limited candidate rows; do not treat raw periods as UTC timestamps.

    Raises if response total exceeds max_rows, to avoid accidental partial-year
    analysis. Returned values are not yet validated observed MW.
    """
    if max_rows < 1:
        raise ValueError("max_rows must be positive")
    rows = []
    offset = 0
    while True:
        response = fetch_json(build_request_url(
            api_key=api_key, respondent=respondent, start=start, end=end,
            offset=offset, length=min(5000, max_rows),
        ))
        total = int(response.get("total", 0))
        if total > max_rows:
            raise ValueError("response exceeds max_rows; narrow scope or raise limit")
        batch = response.get("data")
        if not isinstance(batch, list):
            raise ValueError("EIA response missing data array")
        if not batch and offset < total:
            raise ValueError("empty page before expected total")
        rows.extend(batch)
        offset += len(batch)
        if offset >= total:
            break
    if len(rows) != total:
        raise ValueError("pagination total mismatch")
    return rows
