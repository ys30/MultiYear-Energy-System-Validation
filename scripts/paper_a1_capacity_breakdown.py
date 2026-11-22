"""Paper A1 E1.3: descriptive MW/technology breakdown of unmatched annual keys.

Capacity is a snapshot attribute, not a physical addition/retirement estimate.
"""
import argparse
import csv
import json
from pathlib import Path

URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet"


def calculate(con):
    rows = con.execute(f"""
        WITH base AS (
            SELECT CAST(year(report_date) AS INTEGER) yr,
                   CAST(plant_id_eia AS VARCHAR) plant,
                   CAST(generator_id AS VARCHAR) generator,
                   technology_description AS technology,
                   CAST(capacity_mw AS DOUBLE) capacity_mw
            FROM read_parquet('{URL}')
            WHERE year(report_date) BETWEEN 2023 AND 2025
        ), differences AS (
            SELECT a.yr AS year_a, b.yr AS year_b,
                   'only_in_earlier_year' AS side,
                   CASE WHEN EXISTS (
                        SELECT 1 FROM base other
                        WHERE other.yr=a.yr+1
                          AND other.plant=a.plant)
                        THEN 'plant_present_other_year'
                        ELSE 'plant_absent_other_year' END AS plant_context,
                   coalesce(a.technology,b.technology,'Unknown') AS technology,
                   coalesce(a.capacity_mw,b.capacity_mw) AS capacity_mw
            FROM (SELECT 2023 yr UNION ALL SELECT 2024) y
            JOIN base a ON a.yr=y.yr
            LEFT JOIN base b ON b.yr=a.yr+1 AND b.plant=a.plant AND b.generator=a.generator
            WHERE b.generator IS NULL
            UNION ALL
            SELECT y.yr AS year_a, y.yr+1 AS year_b, 'only_in_later_year',
                   CASE WHEN EXISTS (SELECT 1 FROM base other
                       WHERE other.yr=y.yr AND other.plant=b.plant)
                       THEN 'plant_present_other_year' ELSE 'plant_absent_other_year' END,
                   coalesce(b.technology,'Unknown'), b.capacity_mw
            FROM (SELECT 2023 yr UNION ALL SELECT 2024) y
            JOIN base b ON b.yr=y.yr+1
            LEFT JOIN base a ON a.yr=y.yr AND a.plant=b.plant AND a.generator=b.generator
            WHERE a.generator IS NULL
        )
        SELECT year_a, year_b, side, plant_context, technology,
               count(*) records,
               count(capacity_mw) records_with_capacity,
               sum(CASE WHEN capacity_mw>=0 THEN capacity_mw ELSE NULL END) sum_nonnegative_mw,
               count(*) FILTER (WHERE capacity_mw<0) negative_capacity_records
        FROM differences GROUP BY 1,2,3,4,5 ORDER BY 1,3,4,5
    """).fetchall()
    fields=["year_a","year_b","side","plant_context","technology","records",
            "records_with_capacity","sum_nonnegative_mw","negative_capacity_records"]
    return [dict(zip(fields,row)) for row in rows]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    import duckdb
    con=duckdb.connect()
    rows=calculate(con)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with (args.output_dir/"unmatched_capacity_by_technology.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir/"unmatched_capacity_by_technology.json").write_text(
        json.dumps({"source_url":URL,"interpretation":"snapshot MW of unmatched records; not net capacity change",
                    "rows":rows},indent=2)+"\n")
    print(json.dumps({"groups":len(rows),"records":sum(r["records"] for r in rows)},indent=2))


if __name__=="__main__":
    main()
