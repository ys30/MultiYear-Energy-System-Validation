"""Project A source metadata and fail-closed validation gates."""
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_eia860_source_gates.py"

def run_checker(archive):
    return subprocess.run([sys.executable, str(SCRIPT), "--artifact", str(archive)],
                          capture_output=True, text=True)

def test_archived_metadata_and_unvalidated_gates(tmp_path):
    # Self-contained fixture: test checker logic without requiring an expiring
    # historical GitHub Actions artifact.
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("source_gates", SCRIPT)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    archive = tmp_path / "source.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for year, (digest, size) in mod.EXPECTED.items():
            entries = [{"name": prefix + str(year) + ".xlsx", "bytes": 1}
                       for prefix in mod.REQUIRED]
            record = {"year": year, "sha256": digest, "archive_bytes": size,
                      "entries": entries, "workbook_layouts_recorded": True,
                      **{flag: False for flag in mod.FLAGS}}
            z.writestr(f"{year}/source_inventory.json", json.dumps(record))
    result = run_checker(archive)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["source_metadata_verified"] is True
    assert report["full_fleet_validated"] is False
    assert report["ba_mapping_validated"] is False
    assert report["empirical_dispatch_approved"] is False

def test_tampered_source_checksum_rejected(tmp_path):
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("source_gates", SCRIPT)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    archive = tmp_path / "tampered.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for year, (digest, size) in mod.EXPECTED.items():
            entries = [{"name": prefix + str(year) + ".xlsx", "bytes": 1}
                       for prefix in mod.REQUIRED]
            record = {"year": year, "sha256": ("0" * 64 if year == 2025 else digest),
                      "archive_bytes": size, "entries": entries,
                      "workbook_layouts_recorded": True,
                      **{flag: False for flag in mod.FLAGS}}
            z.writestr(f"{year}/source_inventory.json", json.dumps(record))
    result = run_checker(archive)
    assert result.returncode != 0
    assert "AssertionError" in result.stderr
