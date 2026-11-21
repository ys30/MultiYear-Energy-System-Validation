"""Paper A1 E1: reproducible national PUDL exact-key baseline, not identity truth.

Usage: python scripts/paper_a1_national_baseline.py --output-dir results/paper_a1
Requires duckdb and access to the pinned public PUDL parquet.
"""
import argparse
import csv
import json
from pathlib import Path

RELEASE = "v2026.11.0"
URL = f"https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/{RELEASE}/out_eia__yearly_generators.parquet"
YEARS = (2023, 2024, 2025)


def analyze(connection):
    """Calculate census denominators and adjacent-year exact-ID overlaps."""
    connection.execute(f"""
        CREATE OR REPLACE TEMP VIEW a1_generators AS
        SELECT CAST(year(report_date) AS INTEGER) AS report_year,
               CAST(plant_id_eia AS VARCHAR) AS plant_id_eia,
               CAST(generator_id AS VARCHAR) AS generator_id
        FROM read_parquet('{URL}')
        WHERE year(report_date) BETWEEN 2023 AND 2025
    """)
    duplicate_rows = connection.execute("""
        SELECT report_year, plant_id_eia, generator_id, count(*) AS n
        FROM a1_generators
        GROUP BY 1,2,3 HAVING count(*) > 1
    """).fetchall()
    if duplicate_rows:
        raise ValueError(f"Duplicate exact generator keys within report year: {len(duplicate_rows)}")
    counts = connection.execute("""
        SELECT report_year, count(*) AS n_records,
               count(DISTINCT plant_id_eia) AS n_plants,
               sum(CASE WHEN plant_id_eia IS NULL OR generator_id IS NULL THEN 1 ELSE 0 END) AS null_keys
        FROM a1_generators GROUP BY 1 ORDER BY 1
    """).fetchall()
    if [r[0] for r in counts] != list(YEARS):
        raise ValueError("Pinned parquet does not contain all three expected years")
    if any(r[3] for r in counts):
        raise ValueError("Missing exact generator keys; cannot calculate overlap")
    pairs = connection.execute("""
        SELECT a.report_year AS year_a, b.report_year AS year_b,
               (SELECT count(*) FROM a1_generators x WHERE x.report_year=a.report_year) AS n_a,
               (SELECT count(*) FROM a1_generators x WHERE x.report_year=b.report_year) AS n_b,
               count(*) AS exact_key_overlap
        FROM a1_generators a
        JOIN a1_generators b ON a.plant_id_eia=b.plant_id_eia
             AND a.generator_id=b.generator_id AND b.report_year=a.report_year+1
        GROUP BY 1,2 ORDER BY 1
    """).fetchall()
    # Missing exact keys may reflect ID changes, data coverage or commissioning:
    # they are NOT automatically data errors or physically different generators.
    return {
        "source_release": RELEASE, "source_url": URL,
        "interpretation": "descriptive exact-key continuity, not physical lineage or error prevalence",
        "year_counts": [
            {"report_year": y, "records": n, "plants": p, "null_keys": k}
            for y,n,p,k in counts],
        "adjacent_year_pairs": [
            {"year_a": a, "year_b": b, "records_a": na, "records_b": nb,
             "exact_key_overlap": n,
             "not_matched_from_a": na-n, "not_matched_from_b": nb-n}
            for a,b,na,nb,n in pairs],
        "empirical_dispatch_approved": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    import duckdb
    con = duckdb.connect()
    result = analyze(con)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "national_exact_key_baseline.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (args.output_dir / "national_exact_key_baseline.csv").open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["year_a","year_b","records_a",
                                                  "records_b","exact_key_overlap",
                                                  "not_matched_from_a","not_matched_from_b"])
        writer.writeheader()
        writer.writerows(result["adjacent_year_pairs"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
