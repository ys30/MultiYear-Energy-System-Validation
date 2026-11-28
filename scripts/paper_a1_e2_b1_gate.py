"""Fail-closed E2 B1 decision based on published PUDL identity semantics."""
import argparse
import json
from pathlib import Path

METHODOLOGY="https://docs.catalyst.coop/pudl/en/nightly/methodology/entity_resolution.html"
DICTIONARY="https://docs.catalyst.coop/pudl/en/latest/data_dictionaries/pudl_db.html"

def decide(probe):
    if probe.get("canonical_identity_verified") is not False:
        raise ValueError("Unexpected schema-probe status: requires manual review")
    names={c["name"] for c in probe["candidate_identity_and_provenance_columns"]}
    if not {"plant_id_eia","generator_id"}.issubset(names):
        raise ValueError("B0 EIA keys absent: investigate source schema")
    return {
        "baseline":"B1",
        "status":"unavailable_for_cross_eia_id_physical_generator_linkage",
        "source_url":probe["source_url"],
        "schema_column_count":probe["all_column_count"],
        "observed_identifier_fields":sorted(names),
        "documented_generator_entity_key":["plant_id_eia","generator_id"],
        "physical_identity_links_claimed":0,
        "published_methodology":METHODOLOGY,
        "field_definitions":DICTIONARY,
        "rationale":"PUDL generator canonicalization uses the EIA generator key; unit_id_pudl is dynamic and not independent physical-generator lineage evidence.",
        "next_step":"Collect primary-source EIA documentation and independent adjudication for B2."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    probe=json.loads((folder/"e2_pudl_entity_schema_probe.json").read_text())
    decision=decide(probe)
    (folder/"e2_b1_baseline_decision.json").write_text(json.dumps(decision,indent=2)+"\n")
    print(json.dumps({"baseline":decision["baseline"],"status":decision["status"],
                      "physical_identity_links_claimed":0},indent=2))

if __name__=="__main__":
    main()
