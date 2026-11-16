import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/pudl_annual_generator_presence.py"
TARGETS = ROOT / "data/pudl/project_a_pudl_29_targets.csv"

def execute(tmp_path, lines, sha_override=None):
    annual = tmp_path / "annual.csv"
    annual.write_text("plant_id_eia,generator_id,report_date\n" + lines)
    digest = hashlib.sha256(annual.read_bytes()).hexdigest()
    output = tmp_path / "result.json"
    cmd = [sys.executable, str(SCRIPT), "--targets", str(TARGETS),
           "--annual-csv", str(annual), "--release", "v2026.11.0",
           "--sha256", sha_override or digest, "--output", str(output)]
    return subprocess.run(cmd, capture_output=True, text=True), output

def test_annual_presence_three_years(tmp_path):
    with TARGETS.open(newline="") as f:
        a, b = list(csv.DictReader(f))[:2]
    lines = (f"{a['plant_id_eia']},{a['generator_id']},2023-12-31\n"
             f"{a['plant_id_eia']},{a['generator_id']},2025-12-31\n"
             f"{b['plant_id_eia']},{b['generator_id']},2024-12-31\n")
    proc, output = execute(tmp_path, lines)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(output.read_text())
    assert result["present_by_year"] == {"2023": 1, "2024": 1, "2025": 1}
    assert result["missing_by_year"] == {"2023": 28, "2024": 28, "2025": 28}
    assert result["pudl_changelog_matched"] is False
    assert result["physical_commissioning_verified"] is False

def test_rejects_duplicate_annual_key(tmp_path):
    with TARGETS.open(newline="") as f:
        a = next(csv.DictReader(f))
    line = f"{a['plant_id_eia']},{a['generator_id']},2024-12-31\n"
    proc, output = execute(tmp_path, line + line)
    assert proc.returncode != 0
    assert "Duplicate plant/generator/year" in proc.stderr
    assert not output.exists()

def test_rejects_bad_sha(tmp_path):
    proc, output = execute(tmp_path, "50535,MWD1,2024-12-31\n", "0" * 64)
    assert proc.returncode != 0
    assert "SHA256 mismatch" in proc.stderr
    assert not output.exists()

def test_rejects_bad_date(tmp_path):
    proc, output = execute(tmp_path, "50535,MWD1,2024-99-99\n")
    assert proc.returncode != 0
    assert "Invalid annual row" in proc.stderr
    assert not output.exists()
