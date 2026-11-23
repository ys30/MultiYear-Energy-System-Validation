"""Create E2 source-evidence collection sheet; no evidence is fabricated."""
import argparse
import csv
import json
from pathlib import Path

FIELDS=["year_a","year_b","side","plant_context","plant_id_eia","generator_id",
        "report_year","pudl_source_url","official_product","official_vintage",
        "official_archive_url","official_archive_sha256","official_sheet",
        "official_row_locator","official_generator_id","official_status",
        "official_capacity_mw","lineage_statement_quote_or_locator",
        "relationship_claim","evidence_strength","collector","collected_at_utc",
        "reviewer_1_decision","reviewer_2_decision","adjudicated_decision","notes"]
DECISIONS=("verified_same_physical_unit","documented_successor","distinct_units",
           "conflicting_evidence","unresolved")

def build(queue,source):
    result=[]
    for r in queue:
        row={k:"" for k in FIELDS}
        for k in ("year_a","year_b","side","plant_context","plant_id_eia",
                  "generator_id","report_year"):
            row[k]=r[k]
        row["pudl_source_url"]=source
        result.append(row)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    folder=args.output_dir
    manifest=json.loads((folder/"e2_review_queue_manifest.json").read_text())
    with (folder/"e2_blinded_review_queue.csv").open(newline="") as f:
        queue=list(csv.DictReader(f))
    rows=build(queue,manifest["source_url"])
    with (folder/"e2_official_evidence_collection.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    instructions={"status":"uncollected","rows":len(rows),"source":manifest["source_url"],
      "allowed_adjudication_labels":DECISIONS,
      "rule":"Never fill official fields without inspecting and locating the exact EIA archive record. Do not infer lineage from plant, capacity, status, or dates alone.",
      "requirement":"Record official archive URL, SHA256, source vintage, sheet and row locator; dual-review before adjudication."}
    (folder/"e2_evidence_collection_instructions.json").write_text(json.dumps(instructions,indent=2)+"\n")
    print(f"E2 official-evidence template created for {len(rows)} sampled records; no official evidence or adjudication asserted")

if __name__=="__main__":
    main()
