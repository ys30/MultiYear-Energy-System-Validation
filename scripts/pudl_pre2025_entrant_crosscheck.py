"""PUDL changelog cross-check. Supports local CSV input and optional DuckDB Parquet.

No remote download. A changelog row is NOT a monthly snapshot, nor proof of commissioning.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as src:
        for chunk in iter(lambda: src.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def read_targets(path):
    with open(path, newline="") as src:
        rows = list(csv.DictReader(src))
    required = {"plant_id_eia", "generator_id", "reported_operating_year",
                "status_2025", "op_nameplate_mw_2025"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Target CSV schema invalid")
    if len(rows) != 29:
        raise ValueError(f"Expected 29 targets, got {len(rows)}")
    keys = [(int(r["plant_id_eia"]), r["generator_id"].strip()) for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate target keys")
    if any(int(r["reported_operating_year"]) >= 2025 for r in rows):
        raise ValueError("Target year is not pre-2025")
    op = sum(float(r["op_nameplate_mw_2025"]) for r in rows
             if r["status_2025"] == "OP")
    if abs(op - 138.1) > 0.01:
        raise ValueError(f"Expected 138.1 MW OP, got {op}")
    return rows, keys

def read_changes(path):
    p = Path(path)
    if p.suffix.lower() == ".csv":
        with open(p, newline="") as src:
            return list(csv.DictReader(src))
    if p.suffix.lower() == ".parquet":
        try:
            import duckdb
        except ImportError as exc:
            raise RuntimeError("Install duckdb to read local Parquet") from exc
        con = duckdb.connect()
        try:
            return [dict(zip([x[0] for x in cur.description], row))
                    for cur in [con.execute(
                        "SELECT plant_id_eia, generator_id, report_date FROM read_parquet(?)",
                        [str(p)])] for row in cur.fetchall()]
        finally:
            con.close()
    raise ValueError("PUDL input must be local CSV or Parquet")

def audit(targets, pudl, output, release, expected_sha256=None):
    target_rows, keys = read_targets(targets)
    if not release or release.lower() in {"latest", "nightly"}:
        raise ValueError("Specify an immutable PUDL release version")
    digest = sha256(pudl)
    if not expected_sha256 and not release.startswith("fixture-"):
        raise ValueError("Real PUDL input requires a pinned --sha256 checksum")
    if expected_sha256 and digest.lower() != expected_sha256.lower():
        raise ValueError("PUDL SHA256 mismatch")
    # Parquet source can contain millions of changelog rows; restrict to target keys
    # in DuckDB before materializing. CSV fixtures retain full-source validation.
    if Path(pudl).suffix.lower() == ".parquet":
        import duckdb
        con = duckdb.connect()
        try:
            con.execute("CREATE TEMP TABLE target_keys (plant_id_eia BIGINT, generator_id VARCHAR)")
            con.executemany("INSERT INTO target_keys VALUES (?, ?)", keys)
            cursor = con.execute("""
                SELECT p.plant_id_eia, p.generator_id, p.report_date
                FROM read_parquet(?) AS p
                INNER JOIN target_keys AS t
                  ON p.plant_id_eia = t.plant_id_eia
                 AND CAST(p.generator_id AS VARCHAR) = t.generator_id
            """, [str(pudl)])
            rows = [dict(zip([x[0] for x in cursor.description], r))
                    for r in cursor.fetchall()]
        finally:
            con.close()
        if not rows:
            raise ValueError("No target keys matched PUDL Parquet; verify schema and release")
    else:
        rows = read_changes(pudl)
    required = {"plant_id_eia", "generator_id", "report_date"}
    if not rows:
        raise ValueError("PUDL changelog is empty; refusing inconclusive match")
    if not required.issubset(rows[0]):
        raise ValueError("PUDL changelog schema missing required columns")
    changes = defaultdict(list)
    target_key_set = set(keys)
    seen = set()
    for row in rows:
        key = (int(row["plant_id_eia"]), str(row["generator_id"]).strip())
        date = str(row["report_date"])[:10]
        from datetime import date as calendar_date
        try:
            calendar_date.fromisoformat(date)
        except ValueError as exc:
            raise ValueError(f"Invalid PUDL report_date: {date}") from exc
        if (key, date) in seen:
            raise ValueError(f"Duplicate changelog primary key: {key}, {date}")
        seen.add((key, date))
        if key in target_key_set:
            changes[key].append(date)
    results = []
    for row, key in zip(target_rows, keys):
        dates = sorted(changes[key])
        results.append({
            "plant_id_eia": key[0], "generator_id": key[1],
            "reported_operating_year": int(row["reported_operating_year"]),
            "status_2025": row["status_2025"],
            "op_nameplate_mw_2025": float(row["op_nameplate_mw_2025"]),
            "first_changelog_date": dates[0] if dates else None,
            "last_changelog_date": dates[-1] if dates else None,
            "pre2025_change_count": sum(d < "2025-01-01" for d in dates),
            "changelog_rows": len(dates),
            "interpretation": "matched_changelog_not_monthly_presence" if dates
                else "no_changelog_match_not_proof_of_absence",
        })
    out = {
        "pudl_release": release, "pudl_file_sha256": digest,
        "target_file_sha256": sha256(targets), "source_rows": len(rows),
        "targets": len(results),
        "matched": sum(r["changelog_rows"] > 0 for r in results),
        "with_pre2025_changelog": sum(r["pre2025_change_count"] > 0 for r in results),
        "unmatched": sum(r["changelog_rows"] == 0 for r in results),
        "records": results,
        "source_independence": "PUDL EIA-860M transforms EIA reports; not independent physical evidence",
        "causal_status": "unresolved", "empirical_dispatch_approved": False,
        "source_sha256_verified": bool(expected_sha256),
        "pudl_matched": bool(expected_sha256) and not release.startswith("fixture-") and len(rows) > 0,
        "data_is_fixture": release.startswith("fixture-"),
    }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(out, indent=2) + "\n")
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--targets", required=True)
    p.add_argument("--pudl", required=True, help="Local CSV or Parquet")
    p.add_argument("--release", required=True)
    p.add_argument("--sha256", default=None)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    print(json.dumps({k:v for k,v in audit(a.targets,a.pudl,a.output,
          a.release,a.sha256).items() if k not in {"records"}}, indent=2))
