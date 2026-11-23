"""Fail-closed checks: E2 evidence sheet has exact queue keys and no fabricated evidence."""
import argparse
import csv
import json
from pathlib import Path

KEYS=("year_a","year_b","side","plant_context","plant_id_eia","generator_id","report_year")
EVIDENCE=("official_product","official_vintage","official_archive_url",
          "official_archive_sha256","official_sheet","official_row_locator",
          "official_generator_id","official_status","official_capacity_mw",
          "lineage_statement_quote_or_locator","relationship_claim",
          "evidence_strength","collector","collected_at_utc",
          "reviewer_1_decision","reviewer_2_decision","adjudicated_decision","notes")

def check(queue, sheet, instructions, source):
    if len(queue)!=len(sheet) or len(sheet)!=instructions["rows"]:
        raise ValueError("E2 evidence row count mismatch")
    if instructions["status"]!="uncollected" or instructions["source"]!=source:
        raise ValueError("Evidence provenance/status invalid")
    a=[tuple(row[k] for k in KEYS) for row in queue]
    b=[tuple(row[k] for k in KEYS) for row in sheet]
    if a!=b or len(set(b))!=len(b):
        raise ValueError("Evidence sheet does not preserve unique sampled keys and order")
    for row in sheet:
        if row["pudl_source_url"]!=source:
            raise ValueError("PUDL source mismatch")
        if any(row[k].strip() for k in EVIDENCE):
            raise ValueError("Unreviewed official evidence or adjudication was prefilled")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    with (folder/"e2_blinded_review_queue.csv").open(newline="") as f:
        queue=list(csv.DictReader(f))
    with (folder/"e2_official_evidence_collection.csv").open(newline="") as f:
        sheet=list(csv.DictReader(f))
    instructions=json.loads((folder/"e2_evidence_collection_instructions.json").read_text())
    manifest=json.loads((folder/"e2_review_queue_manifest.json").read_text())
    check(queue,sheet,instructions,manifest["source_url"])
    print(f"E2 evidence template verified: {len(sheet)} keys, zero fabricated source assertions")

if __name__=="__main__":
    main()
