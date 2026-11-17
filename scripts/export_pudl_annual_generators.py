"""Export PUDL's fixed-version annual generator Parquet to the audited CSV schema.

Usage:
 python scripts/export_pudl_annual_generators.py --release v2026.11.0 \
   --output /secure/path/annual_generators.csv

Requires: pip install duckdb. Source is a public, versioned PUDL Parquet table.
This is a source export, NOT commissioning verification.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", required=True)
    parser.add_argument("--table", default="out_eia__yearly_generators")
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-url", help="Exact verified versioned Parquet URL; defaults to release/table S3 path")
    parser.add_argument("--expected-parquet-sha256", help="Optional independent checksum of downloaded Parquet; remote range scans cannot validate it")
    args = parser.parse_args()
    if not re.fullmatch(r"v[0-9]{4}\.[0-9]{1,2}\.[0-9]+", args.release):
        parser.error("Use a fixed PUDL release such as v2026.11.0")
    if not re.fullmatch(r"[a-z][a-z0-9_]+", args.table):
        parser.error("Invalid table name")
    try:
        import duckdb
    except ImportError as exc:
        parser.error("Install duckdb before running this export")
    url = args.source_url or f"https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/{args.release}/{args.table}.parquet"
    if not re.fullmatch(r"https://[a-zA-Z0-9.-]+/[a-zA-Z0-9_./-]+\.parquet", url) or f"/{args.release}/" not in url:
        parser.error("Source must be an HTTPS Parquet URL containing the pinned release")
    if args.expected_parquet_sha256:
        parser.error("Parquet byte checksums require a local verified download; remote scans cannot validate this flag")
    con = duckdb.connect()
    try:
        columns = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{url}')").fetchall()]
        needed = {"plant_id_eia", "generator_id", "report_date"}
        if not needed.issubset(columns):
            raise ValueError(f"Annual table missing columns: {sorted(needed - set(columns))}")
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".partial")
        count = 0
        by_year = {str(y): 0 for y in (2023, 2024, 2025)}
        query = (f"SELECT plant_id_eia, generator_id, report_date FROM read_parquet('{url}') "
                 "WHERE year(report_date) BETWEEN 2023 AND 2025 "
                 "ORDER BY report_date, plant_id_eia, generator_id")
        with temporary.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("plant_id_eia", "generator_id", "report_date"))
            cursor = con.execute(query)
            while batch := cursor.fetchmany(10000):
                for plant, generator, report_date in batch:
                    writer.writerow((plant, generator, report_date.isoformat()))
                    by_year[str(report_date.year)] += 1
                    count += 1
        if any(not n for n in by_year.values()):
            temporary.unlink(missing_ok=True)
            raise ValueError(f"Annual source missing year(s): {by_year}")
        checksum = hashlib.sha256(temporary.read_bytes()).hexdigest()
        manifest = {"source_url": url, "release": args.release, "table": args.table,
                    "sha256": checksum, "rows": count, "rows_by_year": by_year,
                    "physical_commissioning_verified": False,
                    "empirical_dispatch_approved": False}
        temporary.replace(output)
        output.with_suffix(output.suffix + ".provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(manifest, indent=2))
    finally:
        con.close()


if __name__ == "__main__":
    main()
