"""E2: reproducible stratified review queue, NOT identity adjudication.

A deterministic census-based sample of unmatched exact keys, with source-year
attributes and blank independent-review fields. No candidate physical crosswalks.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

URL="https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet"
YEARS=((2023,2024),(2024,2025))
SIDES=("only_in_earlier_year","only_in_later_year")
CONTEXTS=("plant_present_other_year","plant_absent_other_year")
SEED="paper-a1-e2-stratified-v1"
FIELDS=["year_a","year_b","side","plant_context","plant_id_eia","generator_id",
        "report_year","technology_description","capacity_mw","operational_status",
        "stratum_population","sample_n","selection_probability","selection_rank",
        "reviewer_1_decision","reviewer_2_decision","adjudicated_decision",
        "primary_source_url","source_row_locator","review_notes"]


def sample(con, per_stratum=20):
    con.execute(f"""
      CREATE OR REPLACE TEMP VIEW e2_base AS
      SELECT CAST(year(report_date) AS INTEGER) yr,
             CAST(plant_id_eia AS VARCHAR) plant,
             CAST(generator_id AS VARCHAR) generator,
             technology_description technology,
             CAST(capacity_mw AS DOUBLE) capacity_mw,
             operational_status status
      FROM read_parquet('{URL}')
      WHERE year(report_date) BETWEEN 2023 AND 2025
    """)
    records=[]
    population=[]
    for a,b in YEARS:
        for side in SIDES:
            src,dst=(a,b) if side=="only_in_earlier_year" else (b,a)
            rows=con.execute("""
                SELECT s.plant,s.generator,s.technology,s.capacity_mw,s.status,
                  CASE WHEN EXISTS (SELECT 1 FROM e2_base d
                                    WHERE d.yr=? AND d.plant=s.plant)
                    THEN 'plant_present_other_year'
                    ELSE 'plant_absent_other_year' END context
                FROM e2_base s
                WHERE s.yr=?
                  AND NOT EXISTS (SELECT 1 FROM e2_base d
                                  WHERE d.yr=? AND d.plant=s.plant AND d.generator=s.generator)
            """,[dst,src,dst]).fetchall()
            for context in CONTEXTS:
                group=[r for r in rows if r[5]==context]
                n=min(per_stratum,len(group))
                ordered=sorted(group,key=lambda r:hashlib.sha256(
                    f"{SEED}|{a}|{b}|{side}|{context}|{r[0]}|{r[1]}".encode()).hexdigest())
                population.append({"year_a":a,"year_b":b,"side":side,
                                   "plant_context":context,"population":len(group),"sampled":n})
                for rank,r in enumerate(ordered[:n],start=1):
                    records.append(dict(zip(FIELDS,[
                        a,b,side,context,r[0],r[1],src,r[2],r[3],r[4],
                        len(group),n,n/len(group),rank,"","","","","",""
                    ])))
    return records,population


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--per-stratum",type=int,default=20)
    args=p.parse_args()
    if args.per_stratum<1:
        p.error("--per-stratum must be positive")
    import duckdb
    records,population=sample(duckdb.connect(),args.per_stratum)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with (args.output_dir/"e2_blinded_review_queue.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    manifest={"source_url":URL,"seed":SEED,"per_stratum_target":args.per_stratum,
              "strata":population,"sampled_total":len(records),
              "adjudicated_count":0,"identity_links_claimed":0,
              "note":"Queue only; sample inclusion probabilities apply within each stratum. Reviewer fields are blank."}
    (args.output_dir/"e2_review_queue_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
