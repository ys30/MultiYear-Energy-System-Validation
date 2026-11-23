"""E2 B1: inspect pinned PUDL generator entity-resolution fields, without assuming lineage.

Schema-only probe. Never interpret a canonical PUDL ID as verified physical identity.
"""
import argparse
import json
from pathlib import Path

URL="https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet"
SEARCH=("generator_id","plant_id","entity","record_id","report_date","capacity_mw",
        "operational_status","technology_description")

def inspect(con):
    columns=con.execute(f"DESCRIBE SELECT * FROM read_parquet('{URL}')").fetchall()
    found=[{"name":str(r[0]),"type":str(r[1])} for r in columns
           if any(word in str(r[0]).lower() for word in SEARCH)]
    return {"source_url":URL,"all_column_count":len(columns),
            "candidate_identity_and_provenance_columns":found,
            "canonical_identity_verified":False,
            "note":"Column names alone do not prove PUDL cross-vintage physical lineage. Inspect entity tables and documentation before defining B1."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    import duckdb
    result=inspect(duckdb.connect())
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"e2_pudl_entity_schema_probe.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
