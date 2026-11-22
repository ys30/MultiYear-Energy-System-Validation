"""E1.2: classify unmatched exact generator keys by plant presence.

Run: python scripts/paper_a1_unmatched_classification.py --output-dir results/paper_a1
Labels are record-coverage categories, NOT generator identity or physical events.
"""
import argparse
import csv
import json
from pathlib import Path

RELEASE = "v2026.11.0"
URL = f"https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/{RELEASE}/out_eia__yearly_generators.parquet"
YEARS = (2023, 2024, 2025)


def classify(con):
    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW a1_keys AS
        SELECT CAST(year(report_date) AS INTEGER) AS yr,
               CAST(plant_id_eia AS VARCHAR) AS plant,
               CAST(generator_id AS VARCHAR) AS generator
        FROM read_parquet('{URL}')
        WHERE year(report_date) BETWEEN 2023 AND 2025
    """)
    out = []
    for a, b in zip(YEARS[:-1], YEARS[1:]):
        # Source-only at an absent plant is a plant-coverage difference.
        # Source-only at a shared plant is an ID-level difference; not proof of renaming.
        rows = con.execute("""
            WITH older AS (
              SELECT plant, generator FROM a1_keys WHERE yr=?
            ), newer AS (
              SELECT plant, generator FROM a1_keys WHERE yr=?
            ), missing_older AS (
              SELECT o.plant, o.generator
              FROM older o ANTI JOIN newer n USING (plant, generator)
            ), missing_newer AS (
              SELECT n.plant, n.generator
              FROM newer n ANTI JOIN older o USING (plant, generator)
            ), classified AS (
              SELECT 'only_in_earlier_year' AS side,
                     CASE WHEN EXISTS (SELECT 1 FROM newer n WHERE n.plant=m.plant)
                          THEN 'plant_present_other_year'
                          ELSE 'plant_absent_other_year' END AS plant_context
              FROM missing_older m
              UNION ALL
              SELECT 'only_in_later_year',
                     CASE WHEN EXISTS (SELECT 1 FROM older o WHERE o.plant=m.plant)
                          THEN 'plant_present_other_year'
                          ELSE 'plant_absent_other_year' END
              FROM missing_newer m
            )
            SELECT side, plant_context, count(*) AS n
            FROM classified GROUP BY 1,2 ORDER BY 1,2
        """, [a,b]).fetchall()
        for side, context, n in rows:
            out.append({"year_a":a,"year_b":b,"side":side,
                        "plant_context":context,"records":n})
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    import duckdb
    rows=classify(duckdb.connect())
    # Exhaustive side totals are checked against the exact-key census in the
    # main workflow's next reconciliation stage.
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"unmatched_plant_context.json").write_text(
        json.dumps({"source_url":URL,"classification":rows,
                    "physical_lineage_inferred":False},indent=2)+"\n")
    with (args.output_dir/"unmatched_plant_context.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["year_a","year_b","side","plant_context","records"])
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(rows,indent=2))


if __name__=="__main__":
    main()
