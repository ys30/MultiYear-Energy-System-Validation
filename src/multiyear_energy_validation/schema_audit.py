"""Inspect EIA candidate JSON structure without asserting semantic validity."""
import json
from collections import Counter
from pathlib import Path
from datetime import datetime, timedelta


def summarize_candidate_schema(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty list required")
    if any(not isinstance(r, dict) for r in rows):
        raise ValueError("all rows must be objects")
    keys = sorted(set().union(*(r.keys() for r in rows)))
    examples = {}
    for field in ("period", "respondent", "type", "units", "value-units"):
        if field in keys:
            values = [str(r.get(field)) for r in rows]
            counts = Counter(values)
            examples[field] = {
                "distinct_count": len(counts),
                "sample_values": sorted(counts)[:10],
            }
    return {
        "row_count": len(rows),
        "field_names": keys,
        "field_presence_counts": {k: sum(k in r for r in rows) for k in keys},
        "categorical_examples": examples,
        "sample_periods": [str(r.get("period")) for r in rows[:3]],
        "verification_status": "schema_inspected_semantics_not_verified",
    }


def audit_candidate_file(input_path, output_path):
    rows = json.loads(Path(input_path).read_text(encoding="utf-8"))
    report = summarize_candidate_schema(rows)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    return report


def audit_period_label_grid(rows, *, year):
    """Audit raw API period labels against requested calendar-hour labels.

    This does not interpret labels as interval starts or ends, nor certify UTC.
    """
    if not isinstance(year, int) or year < 1900:
        raise ValueError("invalid year")
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    expected = set()
    current = start
    while current < end:
        expected.add(current.strftime("%Y-%m-%dT%H"))
        current += timedelta(hours=1)
    labels = [str(r.get("period")) for r in rows]
    counts = Counter(labels)
    observed = set(labels)
    return {
        "year": year,
        "expected_labels": len(expected),
        "observed_rows": len(labels),
        "distinct_labels": len(observed),
        "missing_labels": sorted(expected - observed),
        "unexpected_labels": sorted(observed - expected),
        "duplicate_labels": {k: v for k, v in sorted(counts.items()) if v > 1},
        "interpretation": "raw_period_labels_only_not_verified_utc_intervals",
    }


def candidate_year_acceptance(grid):
    """Conservative raw-label gate; passing does NOT certify EIA interval semantics.

    A failed gate prevents a candidate year being described as complete or
    accepted for modeling. Missing hours must never be silently interpolated.
    """
    missing = grid["missing_labels"]
    unexpected = grid["unexpected_labels"]
    duplicates = grid["duplicate_labels"]
    valid_count = grid["distinct_labels"] == grid["expected_labels"]
    accepted = not (missing or unexpected or duplicates) and valid_count
    return {
        "candidate_label_grid_complete": accepted,
        "model_input_approved": False,
        "reason": ("raw_label_grid_complete_semantic_validation_still_required"
                   if accepted else "incomplete_or_invalid_raw_hourly_label_grid"),
        "missing_labels": missing,
        "unexpected_labels": unexpected,
        "duplicate_labels": duplicates,
        "imputation_performed": False,
    }
