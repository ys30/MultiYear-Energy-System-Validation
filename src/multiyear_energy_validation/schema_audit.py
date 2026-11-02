"""Inspect EIA candidate JSON structure without asserting semantic validity."""
import json
from collections import Counter
from pathlib import Path


def summarize_candidate_schema(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty list required")
    if any(not isinstance(r, dict) for r in rows):
        raise ValueError("all rows must be objects")
    keys = sorted(set().union(*(r.keys() for r in rows)))
    examples = {}
    for field in ("period", "respondent", "type", "units"):
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
