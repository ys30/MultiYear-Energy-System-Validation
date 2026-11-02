"""Persist unverified EIA API candidate rows with a provenance manifest.

Raw provider records are stored locally only; no time or demand semantics are inferred.
"""
import hashlib
import json
from pathlib import Path

from .eia_api import fetch_candidate_pages


def save_candidate_snapshot(output_dir, *, api_key, respondent, start, end,
                            retrieved_at, max_rows=20000):
    """Save candidate records and manifest without exposing the API key."""
    if not retrieved_at:
        raise ValueError("retrieved_at required")
    rows = fetch_candidate_pages(
        api_key=api_key, respondent=respondent, start=start,
        end=end, max_rows=max_rows,
    )
    if not rows:
        raise ValueError("empty candidate response; no snapshot written")
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(rows, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    raw_path = folder / "eia930_candidate_rows.json"
    raw_path.write_bytes(raw)
    manifest = {
        "provider": "U.S. EIA API v2",
        "endpoint": "https://api.eia.gov/v2/electricity/rto/region-data/data/",
        "respondent": respondent, "start": start, "end": end,
        "retrieved_at": retrieved_at, "row_count": len(rows),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "unverified_candidate_not_for_empirical_results",
        "schema_verified": False, "interval_convention_verified": False,
        "observed_demand_definition_verified": False,
    }
    (folder / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
