"""Extract real pinned PUDL annual generator records for the Project A 29-key cohort.

No fixtures, inferred matches, or silent fallback. Preserve remote source URI
and exact extracted CSV hash; a remote Parquet checksum is NOT claimed.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import duckdb
from pudl_pre2025_entrant_crosscheck import read_targets
from pudl_annual_generator_presence import run as audit_annual

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    ap.add_argument("--release", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    if args.release != "v2026.11.0":
        raise ValueError("Release must be explicitly reviewed before changing")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    url = f"https://pudl.catalyst.coop/{args.release}/out_eia__yearly_generators.parquet"
    provenance = {"release": args.release, "source_url": url,
                  "remote_parquet_sha256_verified": False,
                  "query_success": False, "empirical_dispatch_approved": False}
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    _, keys = read_targets(args.targets)
    con = duckdb.connect()
    try:
        con.execute("INSTALL httpfs; LOAD httpfs")
        con.execute("CREATE TEMP TABLE cohort (plant_id_eia BIGINT, generator_id VARCHAR)")
        con.executemany("INSERT INTO cohort VALUES (?, ?)", keys)
        # Confirm actual source schema rather than silently assuming a changelog.
        columns = [x[0] for x in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [url]).fetchall()]
        required = {"plant_id_eia", "generator_id", "report_date"}
        if not required.issubset(columns):
            raise ValueError(f"Unexpected PUDL annual schema: {columns}")
        rows = con.execute("""
            SELECT p.plant_id_eia, CAST(p.generator_id AS VARCHAR), CAST(p.report_date AS VARCHAR)
            FROM read_parquet(?) AS p
            JOIN cohort AS c ON p.plant_id_eia=c.plant_id_eia
              AND CAST(p.generator_id AS VARCHAR)=c.generator_id
            WHERE year(p.report_date) BETWEEN 2023 AND 2025
            ORDER BY 1,2,3
        """, [url]).fetchall()
    finally:
        con.close()
    # A filtered cohort cannot establish coverage of the source years; annual
    # audit's full-year check is deliberately not applied to this extract.
    path = out / "matched_annual_rows.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["plant_id_eia", "generator_id", "report_date"])
        writer.writerows(rows)
    by_year = {str(y): 0 for y in (2023, 2024, 2025)}
    unique = set()
    for plant, generator, dt in rows:
        year = str(dt)[:4]
        key = (plant, generator, year)
        if key in unique:
            raise ValueError(f"Duplicate cohort/year row: {key}")
        unique.add(key)
        by_year[year] += 1
    provenance.update({"query_success": True, "matched_rows": len(rows),
                       "matched_rows_by_year": by_year, "extracted_csv_sha256": sha(path),
                       "source_schema": columns,
                       "full_annual_source_coverage_verified": False,
                       "interpretation": "matched annual rows only; missing rows are not verified absence"})
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))

if __name__ == "__main__":
    main()
