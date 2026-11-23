"""Prepare a bounded B2 review packet without asserting primary-source verification."""
import argparse
import csv
import json
from pathlib import Path

KEYS=("year_a","year_b","side","plant_context","plant_id_eia","generator_id","report_year")
FIELDS=["packet_rank",*KEYS,"capacity_mw","technology_description","operational_status",
        "official_archive_url","official_archive_sha256","official_sheet","official_row_locator",
        "documented_cross_id_link","reviewer_1_decision","reviewer_2_decision",
        "adjudicated_decision","evidence_notes"]
def make_packet(priority,limit):
    if not 1<=limit<=len(priority):
        raise ValueError("Invalid packet limit")
    if len({tuple(r[k] for k in KEYS) for r in priority})!=len(priority):
        raise ValueError("Duplicate sampled key")
    selected=priority[:limit]
    result=[]
    for i,r in enumerate(selected,1):
        out={k:"" for k in FIELDS}
        out["packet_rank"]=str(i)
        for k in (*KEYS,"capacity_mw","technology_description","operational_status"):
            out[k]=r[k]
        result.append(out)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--limit",type=int,default=20)
    args=p.parse_args()
    folder=args.output_dir
    with (folder/"e2_review_priority.csv").open(newline="") as f:
        priority=list(csv.DictReader(f))
    manifest=json.loads((folder/"e2_review_queue_manifest.json").read_text())
    if len(priority)!=manifest["sampled_total"]:
        raise ValueError("Priority queue differs from frozen E2 sample")
    rows=make_packet(priority,args.limit)
    with (folder/"e2_b2_first_review_packet.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    info={"status":"awaiting_official_eia_source_collection","packet_size":len(rows),
          "sampled_population":len(priority),"selection":"first rows of E2 review priority queue",
          "official_evidence_verified":0,"physical_identity_links_claimed":0,
          "note":"Triage packet, not random subsample or evidence of physical generator identity. No claim of review completion."}
    (folder/"e2_b2_first_review_packet_manifest.json").write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps(info,indent=2))
    print("B2 first review packet keys (identifiers only; not identity matches):")
    for row in rows:
        print(f"  #{row['packet_rank']} {row['year_a']}->{row['year_b']} "
              f"{row['side']} plant={row['plant_id_eia']} "
              f"generator={row['generator_id']} report_year={row['report_year']} "
              f"reported_mw={row['capacity_mw']}")

if __name__=="__main__":
    main()
