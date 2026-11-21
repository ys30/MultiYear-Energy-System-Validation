"""Fail-closed evidence gate: Mesa Wind WGNS/MWD1 must not be auto-crosswalked."""
import argparse
import json
from pathlib import Path

PLANT = 50535
HISTORICAL = "WGNS"
TARGET = "MWD1"


def evaluate(evidence):
    """Only an independently verified generator-level lineage can permit mapping.

    Published annual/monthly status, matching plant ID, similar capacity and
    reported operating dates are insufficient for a physical identity claim.
    """
    if evidence.get("plant_id_eia") != PLANT:
        raise ValueError("Unexpected plant ID")
    if evidence.get("historical_generator_id") != HISTORICAL:
        raise ValueError("Unexpected historical generator ID")
    if evidence.get("target_generator_id") != TARGET:
        raise ValueError("Unexpected target generator ID")
    if evidence.get("identity_evidence_type") != "primary_generator_lineage":
        return {"identity_crosswalk_verified": False, "empirical_dispatch_approved": False,
                "reason": "No primary generator-level lineage evidence"}
    if not evidence.get("source_url") or not evidence.get("source_document_sha256"):
        return {"identity_crosswalk_verified": False, "empirical_dispatch_approved": False,
                "reason": "Missing source URL or immutable source digest"}
    if evidence.get("independent_review_status") != "approved":
        return {"identity_crosswalk_verified": False, "empirical_dispatch_approved": False,
                "reason": "Generator lineage has not been independently reviewed"}
    # An approved identity crosswalk is necessary but not sufficient for dispatch.
    return {"identity_crosswalk_verified": True, "empirical_dispatch_approved": False,
            "reason": "Capacity chronology, operational evidence and model inputs require separate review"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    result = evaluate(evidence)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("MESA_IDENTITY_GATE=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
