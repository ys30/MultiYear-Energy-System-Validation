"""Fail-closed checks for E2 deterministic review queue and stratum manifest."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

STRATA_SIDES={"only_in_earlier_year","only_in_later_year"}
STRATA_CONTEXTS={"plant_present_other_year","plant_absent_other_year"}
BLANK_FIELDS=("reviewer_1_decision","reviewer_2_decision","adjudicated_decision",
              "primary_source_url","source_row_locator","review_notes")


def verify(manifest, rows, classification):
    if manifest["source_url"] != classification["source_url"]:
        raise ValueError("Pinned source mismatch")
    expected={(r["year_a"],r["year_b"],r["side"],r["plant_context"]):r["records"]
              for r in classification["classification"]}
    strata={}
    for s in manifest["strata"]:
        key=(s["year_a"],s["year_b"],s["side"],s["plant_context"])
        if key in strata:
            raise ValueError("Duplicate manifest stratum")
        if s["side"] not in STRATA_SIDES or s["plant_context"] not in STRATA_CONTEXTS:
            raise ValueError("Invalid stratum label")
        strata[key]=s
        if s["population"] != expected.get(key,0):
            raise ValueError(f"Population mismatch: {key}")
        if s["sampled"] != min(s["population"],manifest["per_stratum_target"]):
            raise ValueError(f"Incorrect sample size: {key}")
    if len(strata)!=8:
        raise ValueError("Expected eight sampling strata")
    counts=Counter()
    identities=set()
    ranks={}
    for r in rows:
        key=(int(r["year_a"]),int(r["year_b"]),r["side"],r["plant_context"])
        if key not in strata:
            raise ValueError("Unexpected sampled stratum")
        identity=(*key,r["plant_id_eia"],r["generator_id"])
        if identity in identities:
            raise ValueError("Duplicate sampled generator key")
        identities.add(identity)
        counts[key]+=1
        rank=int(r["selection_rank"])
        ranks.setdefault(key,set())
        if rank in ranks[key]:
            raise ValueError("Duplicate selection rank")
        ranks[key].add(rank)
        s=strata[key]
        if int(r["stratum_population"])!=s["population"] or int(r["sample_n"])!=s["sampled"]:
            raise ValueError("Sample row metadata mismatch")
        if abs(float(r["selection_probability"])-s["sampled"]/s["population"])>1e-10:
            raise ValueError("Incorrect inclusion probability")
        if any(r[f].strip() for f in BLANK_FIELDS):
            raise ValueError("Queue includes pre-filled adjudication or source claims")
    for key,s in strata.items():
        if counts[key]!=s["sampled"] or ranks.get(key,set())!=set(range(1,s["sampled"]+1)):
            raise ValueError(f"Sample count/rank mismatch: {key}")
    if len(rows)!=manifest["sampled_total"] or manifest["adjudicated_count"]!=0 or manifest["identity_links_claimed"]!=0:
        raise ValueError("Manifest totals or identity claims invalid")
    return True


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    manifest=json.loads((folder/"e2_review_queue_manifest.json").read_text())
    classification=json.loads((folder/"unmatched_plant_context.json").read_text())
    with (folder/"e2_blinded_review_queue.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    verify(manifest,rows,classification)
    print(f"E2 queue verified: {len(rows)} records, {len(manifest['strata'])} strata, no adjudications")


if __name__=="__main__":
    main()
