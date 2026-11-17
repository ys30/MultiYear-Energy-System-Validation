"""Cross-check PUDL annual coverage against fixed official EIA-860 target metadata.

This produces an evidence matrix, not a commissioning inference.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def build_matrix(coverage, targets):
    if coverage.get("input_kind") != "PUDL_annual_generators":
        raise ValueError("Expected annual PUDL generator coverage receipt")
    release = coverage.get("release")
    if not isinstance(release, str) or not release.strip() or release.lower() in ("latest", "nightly") or release.startswith("fixture-"):
        raise ValueError("Immutable non-fixture PUDL release required")
    if coverage.get("empirical_dispatch_approved") is not False:
        raise ValueError("Unsafe coverage receipt")
    if coverage.get("targets_sha256") != file_sha256(targets):
        raise ValueError("Target file SHA256 does not match coverage receipt")
    if not isinstance(coverage.get("source_sha256"), str) or len(coverage["source_sha256"]) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in coverage["source_sha256"]):
        raise ValueError("Invalid annual source SHA256 in receipt")
    with open(targets, newline="", encoding="utf-8-sig") as f:
        source = list(csv.DictReader(f))
    keys = {(int(r["plant_id_eia"]), r["generator_id"].strip()): r for r in source}
    if len(keys) != 29 or len(source) != 29:
        raise ValueError("Expected 29 unique targets")
    rows = []
    seen = set()
    for item in coverage["records"]:
        key = (int(item["plant_id_eia"]), str(item["generator_id"]).strip())
        year = int(item["year"])
        identity = (*key, year)
        if key not in keys or identity in seen or year not in (2023, 2024, 2025):
            raise ValueError("Unexpected or duplicate coverage key/year")
        seen.add(identity)
        official = keys[key]
        rows.append({
            "plant_id_eia": key[0],
            "generator_id": key[1],
            "year": year,
            "reported_operating_year": int(official["reported_operating_year"]),
            "status_2025": official["status_2025"],
            "op_nameplate_mw_2025": float(official["op_nameplate_mw_2025"]),
            "pudl_annual_classification": item["classification"],
            "pudl_exact_match": item["exact_generator_record"],
            "historical_year_before_reported_operation": year < int(official["reported_operating_year"]),
            "interpretation": "annual_record_only_not_commissioning_proof",
        })
    if len(seen) != 87:
        raise ValueError(f"Expected 87 target-year observations, got {len(seen)}")
    return {
        "schema_version": 1,
        "pudl_release": release,
        "source_sha256": coverage["source_sha256"],
        "targets_sha256": coverage["targets_sha256"],
        "target_year_rows": len(rows),
        "rows": rows,
        "physical_commissioning_verified": False,
        "empirical_dispatch_approved": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--coverage-json", required=True)
    p.add_argument("--targets", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    coverage = json.loads(Path(a.coverage_json).read_text())
    result = build_matrix(coverage, a.targets)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {result['target_year_rows']} descriptive target-year rows")


if __name__ == "__main__":
    main()
