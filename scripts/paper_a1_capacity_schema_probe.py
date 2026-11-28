"""Inspect pinned PUDL generator parquet schema before capacity-weighted E1.3.

This intentionally does not guess capacity or technology field names.
"""
import json
import duckdb
from pathlib import Path

URL = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet"


def main():
    con = duckdb.connect()
    rows = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{URL}')").fetchall()
    columns = [{"name": r[0], "type": r[1]} for r in rows]
    candidates = [c for c in columns if any(term in c["name"].lower()
                  for term in ("capacity", "technology", "energy_source", "state", "status", "report_date"))]
    out = {"source_url": URL, "all_columns": columns, "candidate_columns": candidates,
           "capacity_analysis_completed": False}
    folder = Path("results/paper_a1")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "capacity_schema_probe.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"candidate_columns": candidates, "column_count": len(columns)}, indent=2))


if __name__ == "__main__":
    main()
