"""Plant-level index for primary-source B2 review; records are not physical links."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

def build(packet,candidates):
    groups=defaultdict(lambda:{"sample_keys":set(),"candidate_keys":set(),"packet_ranks":set(),
                                "reported_sample_mw":[]})
    for row in packet:
        key=(row["plant_id_eia"],row["year_a"],row["year_b"])
        g=groups[key]
        g["sample_keys"].add((row["report_year"],row["generator_id"]))
        g["packet_ranks"].add(int(row["packet_rank"]))
        try:
            g["reported_sample_mw"].append(float(row["capacity_mw"]))
        except (ValueError,TypeError):
            pass
    for row in candidates:
        p=packet[int(row["packet_rank"])-1]
        key=(p["plant_id_eia"],p["year_a"],p["year_b"])
        groups[key]["candidate_keys"].add((row["other_report_year"],row["candidate_generator_id"]))
    out=[]
    for (plant,ya,yb),g in groups.items():
        out.append({"plant_id_eia":plant,"year_a":ya,"year_b":yb,
                    "sample_record_count":len(g["sample_keys"]),
                    "distinct_other_year_candidate_keys":len(g["candidate_keys"]),
                    "packet_ranks":",".join(map(str,sorted(g["packet_ranks"]))),
                    "sample_generator_ids":",".join(sorted(x[1] for x in g["sample_keys"])),
                    "other_year_generator_ids":",".join(sorted(x[1] for x in g["candidate_keys"])),
                    "sample_reported_capacity_sum_mw":round(sum(g["reported_sample_mw"]),3),
                    "official_source_status":"not_collected",
                    "physical_lineage_status":"unresolved"})
    out.sort(key=lambda r:(-r["sample_record_count"],-r["distinct_other_year_candidate_keys"],
                           int(r["plant_id_eia"]),int(r["year_a"])))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    with (folder/"e2_b2_first_review_packet.csv").open(newline="") as f:
        packet=list(csv.DictReader(f))
    with (folder/"e2_b2_same_plant_candidates.csv").open(newline="") as f:
        candidates=list(csv.DictReader(f))
    if [int(x["packet_rank"]) for x in packet]!=list(range(1,len(packet)+1)):
        raise ValueError("Packet ranks must be contiguous")
    result=build(packet,candidates)
    with (folder/"e2_b2_plant_review_index.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]))
        w.writeheader()
        w.writerows(result)
    summary={"plant_year_pair_groups":len(result),"sampled_records":len(packet),
             "candidate_comparison_rows":len(candidates),
             "official_sources_collected":0,"physical_links_verified":0}
    (folder/"e2_b2_plant_review_index_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    for row in result:
        print(f"plant={row['plant_id_eia']} years={row['year_a']}->{row['year_b']} "
              f"sampled={row['sample_record_count']} "
              f"unique_candidates={row['distinct_other_year_candidate_keys']} "
              f"sample_ids={row['sample_generator_ids']}")

if __name__=="__main__":
    main()
