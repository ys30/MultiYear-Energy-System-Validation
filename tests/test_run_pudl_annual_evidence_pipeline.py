"""Integration tests for the pinned annual evidence pipeline; synthetic fixtures only."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run_pudl_annual_evidence_pipeline.py"
TARGETS = ROOT / "data/pudl/project_a_pudl_29_targets.csv"


def make_source(tmp_path):
    source = tmp_path / "annual.csv"
    with TARGETS.open(newline="") as f:
        targets = list(csv.DictReader(f))
    with source.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("plant_id_eia", "generator_id", "report_date"))
        for year in (2023, 2024, 2025):
            for target in targets:
                writer.writerow((target["plant_id_eia"], target["generator_id"], f"{year}-12-31"))
    return source


def invoke(source, out, checksum):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--annual-csv", str(source),
         "--targets", str(TARGETS), "--release", "v2026.11.0",
         "--sha256", checksum, "--out-dir", str(out)],
        capture_output=True, text=True,
    )


def test_end_to_end_87_rows_fixture_only(tmp_path):
    source = make_source(tmp_path)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    out = tmp_path / "out"
    run = invoke(source, out, digest)
    assert run.returncode == 0, run.stderr
    coverage = json.loads((out / "pudl_annual_coverage.json").read_text())
    matrix = json.loads((out / "pudl_eia860_87_row_evidence_matrix.json").read_text())
    assert coverage["target_exact_matches_by_year"] == {"2023": 29, "2024": 29, "2025": 29}
    assert matrix["target_year_rows"] == 87
    assert matrix["empirical_dispatch_approved"] is False
    assert matrix["physical_commissioning_verified"] is False


def test_reject_bad_pinned_source_hash(tmp_path):
    source = make_source(tmp_path)
    out = tmp_path / "out"
    run = invoke(source, out, "0" * 64)
    assert run.returncode != 0
    assert not (out / "pudl_eia860_87_row_evidence_matrix.json").exists()
