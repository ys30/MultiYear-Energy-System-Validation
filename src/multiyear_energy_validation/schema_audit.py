"""Inspect EIA candidate JSON structure without asserting semantic validity."""
import json
import math
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

def audit_candidate_values(rows, *, respondent="CISO", demand_type="D",
                           expected_units="megawatthours"):
    """Audit raw numeric observations; no MW conversion or time interpretation."""
    invalid = []
    values = []
    for index, row in enumerate(rows):
        try:
            value = float(row["value"])
            valid = (row.get("respondent") == respondent
                     and row.get("type") == demand_type
                     and row.get("value-units") == expected_units
                     and math.isfinite(value) and value >= 0)
        except (KeyError, TypeError, ValueError, OverflowError):
            valid = False
        if valid:
            values.append(value)
        else:
            invalid.append(index)
    return {
        "row_count": len(rows),
        "valid_observation_count": len(values),
        "invalid_observation_count": len(invalid),
        "invalid_row_indices_sample": invalid[:20],
        "min_raw_mwh": min(values) if values else None,
        "max_raw_mwh": max(values) if values else None,
        "all_observations_valid": len(invalid) == 0 and bool(rows),
        "interpretation": "raw_energy_value_audit_only_not_model_input_approval",
    }

def candidate_combined_acceptance(grid, values):
    """Conservative combined raw-label and value gate, never model approval."""
    label = candidate_year_acceptance(grid)
    values_valid = values["all_observations_valid"]
    return {
        "raw_candidate_eligible_for_semantic_review":
            label["candidate_label_grid_complete"] and values_valid,
        "model_input_approved": False,
        "label_grid_complete": label["candidate_label_grid_complete"],
        "all_observations_valid": values_valid,
        "missing_labels": label["missing_labels"],
        "invalid_observation_count": values["invalid_observation_count"],
        "imputation_performed": False,
        "reason": ("raw_checks_passed_semantics_unverified"
                   if label["candidate_label_grid_complete"] and values_valid
                   else "raw_label_or_value_checks_failed"),
    }

def diagnose_candidate_invalid_rows(rows, *, respondent="CISO",
                                    demand_type="D", expected_units="megawatthours"):
    """Describe invalid EIA records without changing or imputing them."""
    details = []
    for i, row in enumerate(rows):
        reasons = []
        if row.get("respondent") != respondent:
            reasons.append("unexpected_respondent")
        if row.get("type") != demand_type:
            reasons.append("unexpected_type")
        if row.get("value-units") != expected_units:
            reasons.append("unexpected_units")
        try:
            value = float(row["value"])
            if not math.isfinite(value):
                reasons.append("nonfinite_value")
            elif value < 0:
                reasons.append("negative_value")
        except (KeyError, ValueError, TypeError, OverflowError):
            reasons.append("missing_or_non_numeric_value")
        if reasons:
            details.append({
                "row_index": i,
                "period": str(row.get("period")),
                "reasons": reasons,
                "raw_value": str(row.get("value")),
                "raw_units": str(row.get("value-units")),
            })
    return {"invalid_count": len(details), "invalid_records": details}


def audit_utc_interval_hypotheses(rows, *, year):
    """Compare UTC start/end interpretations; do not choose one automatically.

    Raw hourly API labels are UTC clock labels. Whether the period denotes
    interval start or end must be independently established by source evidence.
    """
    from datetime import timezone
    if not isinstance(year, int) or isinstance(year, bool) or year < 1900:
        raise ValueError("invalid year")
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    labels = []
    malformed = []
    for i, row in enumerate(rows):
        try:
            label = datetime.strptime(str(row["period"]), "%Y-%m-%dT%H")
            labels.append(label.replace(tzinfo=timezone.utc))
        except (KeyError, ValueError, TypeError):
            malformed.append(i)
    results = {}
    for hypothesis, offset_hours in (("interval_start", 0), ("interval_end", -1)):
        shifted = [stamp + timedelta(hours=offset_hours) for stamp in labels]
        inside = [stamp for stamp in shifted if start <= stamp < end]
        outside = sorted(stamp.isoformat() for stamp in shifted if not start <= stamp < end)
        results[hypothesis] = {
            "inside_requested_year": len(inside),
            "outside_requested_year": len(outside),
            "outside_sample": outside[:5],
            "first_interval_start_utc": min(shifted).isoformat() if shifted else None,
            "last_interval_start_utc": max(shifted).isoformat() if shifted else None,
        }
    return {
        "year": year,
        "raw_row_count": len(rows),
        "malformed_period_rows": malformed[:20],
        "hypotheses": results,
        "selected_hypothesis": None,
        "interval_semantics_verified": False,
        "model_input_approved": False,
    }


def model_year_hour_ending_window(year):
    """Inclusive EIA UTC hour-ending labels for calendar-year interval starts."""
    if not isinstance(year, int) or isinstance(year, bool) or not 1900 <= year < 9999:
        raise ValueError("invalid year")
    return {
        "start": f"{year}-01-01T01",
        "end": f"{year + 1}-01-01T00",
        "year": year,
        "convention": "eia_930_utc_hour_ending",
    }


def audit_model_year_hour_ending_grid(rows, *, year):
    """Audit EIA hour-ending labels for a true interval-start model year."""
    if not isinstance(year, int) or isinstance(year, bool) or not 1900 <= year < 9999:
        raise ValueError("invalid year")
    first = datetime(year, 1, 1, 1)
    last = datetime(year + 1, 1, 1)
    expected = set()
    cursor = first
    while cursor <= last:
        expected.add(cursor.strftime("%Y-%m-%dT%H"))
        cursor += timedelta(hours=1)
    counts = Counter(str(row.get("period")) for row in rows)
    observed = set(counts)
    return {
        "year": year,
        "expected_labels": len(expected),
        "observed_rows": len(rows),
        "distinct_labels": len(observed),
        "missing_labels": sorted(expected - observed),
        "unexpected_labels": sorted(observed - expected),
        "duplicate_labels": {k: v for k, v in sorted(counts.items()) if v > 1},
        "convention": "eia_930_utc_hour_ending",
    }
