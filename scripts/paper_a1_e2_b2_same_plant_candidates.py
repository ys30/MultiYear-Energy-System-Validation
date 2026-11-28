"""Extract adjacent-year same-plant candidate records for E2 review, without claiming lineage."""
import argparse
import csv
import json
from pathlib import Path

URL="https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet"
COLUMNS=["packet_rank","plant_id_eia","sample_generator_id","sample_report_year",
         "other_report_year","candidate_generator_id","candidate_capacity_mw",
         "candidate_technology_description","candidate_operational_status",
         "candidate_is_exact_key","source_url"]
def extract(con,packet):
    con.execute(f"""CREATE OR REPLACE TEMP VIEW annual AS
        SELECT CAST(report_date AS DATE) AS report_date,
               EXTRACT(YEAR FROM CAST(report_date AS DATE))::INTEGER AS yr,
               CAST(plant_id_eia AS VARCHAR) AS plant,
               CAST(generator_id AS VARCHAR) AS generator,
               capacity_mw, technology_description, operational_status
        FROM read_parquet('{URL}')
        WHERE EXTRACT(YEAR FROM CAST(report_date AS DATE)) IN (2023,2024,2025)""")
    out=[]
    for r in packet:
        other=int(r["year_b"]) if int(r["report_year"])==int(r["year_a"]) else int(r["year_a"])
        candidates=con.execute("""SELECT generator,capacity_mw,technology_description,
                operational_status FROM annual
                WHERE plant=? AND yr=? ORDER BY generator""",
                [r["plant_id_eia"],other]).fetchall()
        for gen,mw,tech,status in candidates:
            out.append({"packet_rank":r["packet_rank"],"plant_id_eia":r["plant_id_eia"],
              "sample_generator_id":r["generator_id"],"sample_report_year":r["report_year"],
              "other_report_year":other,"candidate_generator_id":gen,
              "candidate_capacity_mw":mw,"candidate_technology_description":tech,
              "candidate_operational_status":status,
              "candidate_is_exact_key":str(gen==r["generator_id"]).lower(),
              "source_url":URL})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    folder=args.output_dir
    with (folder/"e2_b2_first_review_packet.csv").open(newline="") as f:
        packet=list(csv.DictReader(f))
    import duckdb
    rows=extract(duckdb.connect(),packet)
    with (folder/"e2_b2_same_plant_candidates.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    summary={"packet_size":len(packet),"adjacent_year_same_plant_candidate_rows":len(rows),
             "verified_physical_identity_links":0,
             "warning":"Candidate records are not evidence of physical generator continuity. Official source review is required."}
    (folder/"e2_b2_candidate_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    for r in packet:
        sub=[x for x in rows if x["packet_rank"]==r["packet_rank"]]
        print(f"packet #{r['packet_rank']}: plant={r['plant_id_eia']} "
              f"sample={r['generator_id']} other_year_candidates={len(sub)}")

if __name__=="__main__":
    main()
