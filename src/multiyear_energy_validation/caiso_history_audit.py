"""Independent CAISO Today's Outlook historical demand CSV diagnostic.

This does not assume the CAISO telemetry and EIA-930 demand definitions match.
"""
import csv
import io
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

URL = "https://www.caiso.com/outlook/history/20250731/demand.csv"


def inspect_csv(payload):
    reader = csv.DictReader(io.StringIO(payload))
    headers = reader.fieldnames or []
    rows = list(reader)
    if not rows:
        raise ValueError("empty CAISO historical demand CSV")
    return {
        "source_url": URL,
        "source": "CAISO Today's Outlook historical demand (telemetry)",
        "independent_of_eia930": True,
        "comparison_status": "schema_review_required",
        "columns": headers,
        "row_count": len(rows),
        "sample_first": rows[:2],
        "sample_last": rows[-2:],
        "target_local_window": "2025-07-31 12:00–15:00 America/Los_Angeles",
        "target_utc_hour_start": "2025-07-31T20:00:00+00:00",
        "note": "Do not compare raw MW directly until telemetry scope and time semantics are checked.",
    }


def main():
    request = Request(URL, headers={"User-Agent": "ResearchDataAudit/1.0"})
    with urlopen(request, timeout=40) as response:
        payload = response.read().decode("utf-8-sig")
    print("CAISO_HISTORICAL_DEMAND_AUDIT=" + json.dumps(inspect_csv(payload), sort_keys=True))


if __name__ == "__main__":
    main()
