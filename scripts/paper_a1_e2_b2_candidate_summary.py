"""Summarize E2 same-plant candidate fanout without claiming physical identity."""
import argparse
import csv
import json
from collections import Counter,defaultdict
from pathlib import Path

def summarize(packet,candidates):
    ranks={r["packet_rank"]:r for r in packet}
    fanout=Counter(r["packet_rank"] for r in candidates)
    distinct=set()
    for c in candidates:
        if c["packet_rank"] not in ranks:
            raise ValueError("Candidate references unknown packet rank")
        p=ranks[c["packet_rank"]]
        if c["plant_id_eia"]!=p["plant_id_eia"]:
            raise ValueError("Candidate plant mismatch")
        other=p["year_b"] if p["report_year"]==p["year_a"] else p["year_a"]
        if c["other_report_year"]!=other:
            raise ValueError("Candidate comparison-year mismatch")
        distinct.add((c["plant_id_eia"],c["other_report_year"],c["candidate_generator_id"]))
    return {
      "packet_size":len(packet),
      "candidate_rows":len(candidates),
      "distinct_other_year_plant_generator_keys":len(distinct),
      "records_with_no_same_plant_candidate":sum(fanout[r]==0 for r in ranks),
      "fanout_by_packet_rank":{r:fanout[r] for r in ranks},
      "verified_physical_identity_links":0,
      "interpretation":"Fanout counts potential comparisons, not matched physical generators."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    with (folder/"e2_b2_first_review_packet.csv").open(newline="") as f:
        packet=list(csv.DictReader(f))
    with (folder/"e2_b2_same_plant_candidates.csv").open(newline="") as f:
        candidates=list(csv.DictReader(f))
    summary=summarize(packet,candidates)
    if summary["candidate_rows"]!=130:
        # This is a reproducibility assertion for the frozen v2026.11.0 cohort.
        raise ValueError("Pinned-cohort candidate count drifted")
    (folder/"e2_b2_candidate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
