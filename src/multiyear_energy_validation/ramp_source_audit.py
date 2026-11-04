"""Trace normalized hour-start demand to exact original EIA hour-ending row."""
from datetime import datetime, timedelta, timezone


def audit_raw_hour(rows, *, hour_start_utc, observed_mw):
    stamp = datetime.fromisoformat(hour_start_utc.replace("Z", "+00:00"))
    if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
        raise ValueError("hour_start_utc must be UTC aware")
    period = (stamp + timedelta(hours=1)).strftime("%Y-%m-%dT%H")
    matches = [row for row in rows if row.get("period") == period
               and row.get("respondent") == "CISO" and row.get("type") == "D"]
    result = {
        "hour_start_utc": stamp.isoformat(),
        "expected_raw_period_hour_ending": period,
        "matching_raw_row_count": len(matches),
        "raw_values": [row.get("value") for row in matches],
        "raw_units": [row.get("value-units", row.get("units")) for row in matches],
        "normalized_observed_mw": observed_mw,
        "source_value_matches_normalized": False,
        "source_is_independently_verified": False,
    }
    if len(matches) == 1:
        try:
            result["source_value_matches_normalized"] = (
                float(matches[0]["value"]) == float(observed_mw)
                and result["raw_units"] == ["megawatthours"]
            )
        except (TypeError, ValueError, KeyError):
            pass
    return result
