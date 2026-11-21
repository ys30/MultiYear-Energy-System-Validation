"""Fail-closed evidence gate: Mesa Wind WGNS/MWD1 must not be auto-crosswalked."""
import argparse
import json
import re
from urllib.parse import urlparse
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
    url = evidence.get("source_url")
    digest = evidence.get("source_document_sha256")
    if (not isinstance(url, str) or urlparse(url).scheme != "https"
            or not urlparse(url).netloc or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None):
        return {"identity_crosswalk_verified": False, "empirical_dispatch_approved": False,
                "reason": "Missing or invalid HTTPS source URL / SHA-256 digest"}
    # A source digest and reviewer flag alone do not establish a lineage claim.
    # Require the primary record to explicitly name both generator IDs and
    # document the type of physical relationship being asserted.
    claim = evidence.get("lineage_claim")
    if (not isinstance(claim, dict)
            or claim.get("from_generator_id") != HISTORICAL
            or claim.get("to_generator_id") != TARGET
            or claim.get("relationship") not in
            {"same_physical_generator", "repowered_successor"}):
        return {"identity_crosswalk_verified": False, "empirical_dispatch_approved": False,
                "reason": "Missing explicit generator-level lineage claim"}
    if not evidence.get("source_record_locator"):
        return {"identity_crosswalk_verified": False, "empirical_dispatch_approved": False,
                "reason": "Missing page, table, or record locator for lineage claim"}
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
