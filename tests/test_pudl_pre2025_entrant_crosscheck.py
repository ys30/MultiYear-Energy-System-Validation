import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pudl_pre2025_entrant_crosscheck.py"
TARGETS = ROOT / "data" / "pudl" / "project_a_pudl_29_targets.csv"

def test_targets_invariants():
    with TARGETS.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 29
    assert len({(r["plant_id_eia"], r["generator_id"]) for r in rows}) == 29
    assert sum(r["status_2025"] == "OP" for r in rows) == 23
    assert sum(r["status_2025"] == "OS" for r in rows) == 1
    assert sum(r["status_2025"] == "SB" for r in rows) == 5
    assert abs(sum(float(r["op_nameplate_mw_2025"]) for r in rows if r["status_2025"] == "OP") - 138.1) < 1e-8

def test_changelog_semantics_and_checksum(tmp_path):
    with TARGETS.open(newline="") as f:
        first = next(csv.DictReader(f))
    pudl = tmp_path / "changelog.csv"
    pudl.write_text(
        "plant_id_eia,generator_id,report_date\n"
        f"{first['plant_id_eia']},{first['generator_id']},2024-09-01\n"
        f"{first['plant_id_eia']},{first['generator_id']},2025-03-01\n"
    )
    out = tmp_path / "out.json"
    subprocess.run([sys.executable, str(SCRIPT), "--targets", str(TARGETS),
        "--pudl", str(pudl), "--release", "fixture-immutable-v1",
        "--output", str(out)], check=True)
    result = json.loads(out.read_text())
    assert result["targets"] == 29
    assert result["matched"] == 1
    assert result["with_pre2025_changelog"] == 1
    assert result["unmatched"] == 28
    assert result["empirical_dispatch_approved"] is False
    assert result["records"][0]["pre2025_change_count"] == 1

def test_duplicate_changelog_primary_key_rejected(tmp_path):
    with TARGETS.open(newline="") as f:
        first = next(csv.DictReader(f))
    pudl = tmp_path / "duplicates.csv"
    line = f"{first['plant_id_eia']},{first['generator_id']},2024-09-01\n"
    pudl.write_text("plant_id_eia,generator_id,report_date\n" + line + line)
    proc = subprocess.run([sys.executable, str(SCRIPT), "--targets", str(TARGETS),
        "--pudl", str(pudl), "--release", "fixture-immutable-v1",
        "--output", str(tmp_path / "out.json")], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "Duplicate changelog primary key" in proc.stderr

def test_pudl_checksum_mismatch_rejected(tmp_path):
    with TARGETS.open(newline="") as f:
        first = next(csv.DictReader(f))
    pudl = tmp_path / "changelog.csv"
    pudl.write_text("plant_id_eia,generator_id,report_date\n"
                    f"{first['plant_id_eia']},{first['generator_id']},2024-09-01\n")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--targets", str(TARGETS),
        "--pudl", str(pudl), "--release", "v2026.11.0",
        "--sha256", "0" * 64, "--output", str(tmp_path / "out.json")],
        capture_output=True, text=True)
    assert proc.returncode != 0
    assert "PUDL SHA256 mismatch" in proc.stderr
    assert not (tmp_path / "out.json").exists()

def test_mutable_release_rejected(tmp_path):
    with TARGETS.open(newline="") as f:
        first = next(csv.DictReader(f))
    pudl = tmp_path / "changelog.csv"
    pudl.write_text("plant_id_eia,generator_id,report_date\n"
                    f"{first['plant_id_eia']},{first['generator_id']},2024-09-01\n")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--targets", str(TARGETS),
        "--pudl", str(pudl), "--release", "nightly",
        "--output", str(tmp_path / "out.json")], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "immutable PUDL release" in proc.stderr


def test_empty_pudl_source_rejected(tmp_path):
    pudl = tmp_path / "empty.csv"
    pudl.write_text("plant_id_eia,generator_id,report_date\n")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--targets", str(TARGETS),
        "--pudl", str(pudl), "--release", "v2026.11.0",
        "--output", str(tmp_path / "out.json")], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "PUDL changelog is empty" in proc.stderr
    assert not (tmp_path / "out.json").exists()

def test_invalid_report_date_rejected(tmp_path):
    with TARGETS.open(newline="") as f:
        first = next(csv.DictReader(f))
    pudl = tmp_path / "bad_date.csv"
    pudl.write_text("plant_id_eia,generator_id,report_date\n"
                    f"{first['plant_id_eia']},{first['generator_id']},2024-99-99\n")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--targets", str(TARGETS),
        "--pudl", str(pudl), "--release", "v2026.11.0",
        "--output", str(tmp_path / "out.json")], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "Invalid PUDL report_date" in proc.stderr
    assert not (tmp_path / "out.json").exists()


def test_manuscript_table3_yearly_counts_and_capacity():
    """Protect the source-verified annual-cohort table from silent drift."""
    from collections import defaultdict
    expected = {
        2012: (0, 1, 0, 0.0),
        2014: (2, 0, 0, 3.8),
        2018: (1, 0, 0, 2.3),
        2020: (1, 0, 0, 2.0),
        2021: (5, 0, 0, 7.2),
        2023: (11, 0, 0, 88.1),
        2024: (3, 0, 5, 34.7),
    }
    actual = defaultdict(lambda: [0, 0, 0, 0.0])
    with TARGETS.open(newline="") as f:
        for row in csv.DictReader(f):
            year = int(row["reported_operating_year"])
            status = row["status_2025"]
            assert status in ("OP", "OS", "SB")
            actual[year][("OP", "OS", "SB").index(status)] += 1
            actual[year][3] += float(row["op_nameplate_mw_2025"])
    assert set(actual) == set(expected)
    for year, values in expected.items():
        assert actual[year][:3] == list(values[:3])
        assert abs(actual[year][3] - values[3]) < 1e-8
    assert sum(sum(v[:3]) for v in actual.values()) == 29
    assert abs(sum(v[3] for v in actual.values()) - 138.1) < 1e-8
