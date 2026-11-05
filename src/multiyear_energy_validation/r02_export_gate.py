"""Read exported normalized EIA fuel manifests and enforce conservative R02 gates."""
import csv
import hashlib
import json
from pathlib import Path


def verify_export(csv_path, manifest_path):
    csv_path, manifest_path = Path(csv_path), Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checksum = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if checksum != manifest["sha256"]:
        raise ValueError("SHA-256 mismatch")
    observed = 0
    missing = 0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"period_utc_eia", "fueltype", "observed_generation_mwh",
                    "observation_status", "taxonomy_boundary_flag"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("missing required columns")
        seen = set()
        for row in reader:
            key = (row["period_utc_eia"], row["fueltype"])
            if key in seen:
                raise ValueError("duplicate hour/fuel")
            seen.add(key)
            if row["observation_status"] == "observed":
                float(row["observed_generation_mwh"])
                observed += 1
            elif row["observation_status"] == "not_reported":
                if row["observed_generation_mwh"] not in ("",):
                    raise ValueError("not_reported has numeric value")
                missing += 1
            else:
                raise ValueError("unknown observation status")
    if observed != manifest["observed_record_count"] or missing != manifest["not_reported_count"]:
        raise ValueError("manifest count mismatch")
    if observed + missing != manifest["row_count"]:
        raise ValueError("manifest row count mismatch")
    return {
        "year": manifest["year"],
        "sha256_verified": True,
        "observed_records": observed,
        "not_reported_cells": missing,
        "source_hour_coverage_pass": manifest["source_coverage_pass"],
        "descriptive_fuel_analysis_candidate": True,
        "r02_dispatch_approved": False,
        "reason": "generation is not renewable availability; operational costs, storage and interchange inputs remain unverified",
    }
