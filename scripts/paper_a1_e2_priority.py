"""E2 review prioritization by observable unmatched-record capacity; not identity inference."""
import argparse
import csv
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    folder=args.output_dir
    manifest=json.loads((folder/"e2_review_queue_manifest.json").read_text())
    with (folder/"e2_blinded_review_queue.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=manifest["sampled_total"]:
        raise ValueError("Sample manifest mismatch")
    for r in rows:
        v=r["capacity_mw"]
        r["capacity_priority_mw"]=float(v) if v not in ("",None) and float(v)>=0 else None
        r["review_priority_group"]="within_plant_first" if r["plant_context"]=="plant_present_other_year" else "plant_coverage"
    rows.sort(key=lambda r:(0 if r["review_priority_group"]=="within_plant_first" else 1,
                            -r["capacity_priority_mw"] if r["capacity_priority_mw"] is not None else float("inf"),
                            r["year_a"],r["side"],r["plant_id_eia"],r["generator_id"]))
    columns=["review_order","review_priority_group","capacity_priority_mw"]+[k for k in rows[0] if k not in ("review_priority_group","capacity_priority_mw")]
    with (folder/"e2_review_priority.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        for i,r in enumerate(rows,1):
            writer.writerow({"review_order":i,**r})
    n=sum(r["review_priority_group"]=="within_plant_first" for r in rows)
    print(json.dumps({"sampled_total":len(rows),"within_plant_first":n,
        "plant_coverage_followup":len(rows)-n,
        "warning":"Review ordering is a workload triage only; capacity does not establish physical identity."},indent=2))

if __name__=="__main__":
    main()
