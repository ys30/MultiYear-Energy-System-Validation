"""Cross-check 2025 pre-2025 entrant generator IDs against PUDL EIA-860M changelog.

Input: identity-matched fleet_transitions_2024_2025.json from verified CI artifact.
Remote: pinned PUDL parquet release URL; do not use mutable 'nightly' for publication.
No claim of independent EIA source: PUDL transforms EIA-860M.
"""
import argparse
import json
from pathlib import Path

def audit(transitions, parquet, output):
    import duckdb
    d = json.loads(Path(transitions).read_text())
    entrants = [
        x for x in d["changes"]
        if x["classification"] == "new_to_ciso_inventory"
        and x.get("current_operating_year_raw") is not None
        and int(x["current_operating_year_raw"]) < 2025
    ]
    if len(entrants) != 29:
        raise ValueError(f"Expected 29 earlier-year entrants; got {len(entrants)}")
    con = duckdb.connect()
    con.execute("CREATE TEMP TABLE targets (plant_id BIGINT, generator_id VARCHAR)")
    con.executemany("INSERT INTO targets VALUES (?, ?)", [
        (int(x["plant_id"]), str(x["generator_id"]).strip()) for x in entrants
    ])
    # Parquet path is passed as a bound parameter; source URL/version logged.
    rows = con.execute("""
        SELECT t.plant_id, t.generator_id,
               MIN(p.report_date) AS first_seen,
               MAX(p.report_date) AS last_change,
               COUNT(p.report_date) AS changelog_rows
        FROM targets t
        LEFT JOIN read_parquet(?) p
          ON p.plant_id_eia = t.plant_id AND CAST(p.generator_id AS VARCHAR) = t.generator_id
        GROUP BY 1,2 ORDER BY 1,2
    """, [parquet]).fetchall()
    out = {
        "source_parquet": parquet,
        "interpretation": "PUDL monthly changelog is transformed EIA-860M, not independent field observation",
        "targets": len(entrants),
        "matched": sum(r[2] is not None for r in rows),
        "unmatched": sum(r[2] is None for r in rows),
        "records": [
            {"plant_id": r[0], "generator_id": r[1],
             "first_report_date": str(r[2]) if r[2] is not None else None,
             "last_change_date": str(r[3]) if r[3] is not None else None,
             "changelog_rows": r[4]}
            for r in rows
        ],
        "causal_status": "unresolved",
        "empirical_dispatch_approved": False,
    }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(out, indent=2))
    print(json.dumps({"targets":out["targets"],"matched":out["matched"],"unmatched":out["unmatched"]}))
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--transitions", required=True)
    p.add_argument("--parquet", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    audit(a.transitions, a.parquet, a.output)
