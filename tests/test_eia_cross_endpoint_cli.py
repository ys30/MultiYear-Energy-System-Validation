"""Tests for offline EIA endpoint provenance CLI."""
import json
from pathlib import Path

import pytest

from multiyear_energy_validation.eia_cross_endpoint_cli import main


def test_cli_writes_hashes_and_does_not_modify_raw_inputs(tmp_path: Path):
    region = tmp_path / "region.json"
    fuel = tmp_path / "fuel.json"
    out = tmp_path / "report.json"
    region.write_text(json.dumps([{"period": "2025-07-31T21", "value": 27732}]))
    fuel.write_text(json.dumps([
        {"period": "2025-07-31T21", "fueltype": "OTH", "value": -10},
        {"period": "2025-07-31T21", "fueltype": "NUC", "value": 2271},
        {"period": "2025-07-31T21", "fueltype": "OTHER", "value": 27742},
    ]))
    original = (region.read_bytes(), fuel.read_bytes())
    assert main([
        "--region-json", str(region), "--fuel-json", str(fuel),
        "--output-json", str(out),
        "--region-url", "https://example.org/region",
        "--fuel-url", "https://example.org/fuel",
        "--retrieved-at", "2026-11-10T22:00:00Z",
    ]) == 0
    result = json.loads(out.read_text())
    assert result["rows"][0]["fuel_minus_region_mwh"] == "2271"
    assert len(result["fuel_source"]["sha256"]) == 64
    assert not result["empirical_dispatch_approved"]
    assert (region.read_bytes(), fuel.read_bytes()) == original


def test_cli_rejects_output_overwriting_raw(tmp_path: Path):
    region = tmp_path / "region.json"
    fuel = tmp_path / "fuel.json"
    region.write_text("[]")
    fuel.write_text("[]")
    with pytest.raises(SystemExit):
        main([
            "--region-json", str(region), "--fuel-json", str(fuel),
            "--output-json", str(region),
            "--region-url", "https://example.org/region",
            "--fuel-url", "https://example.org/fuel",
            "--retrieved-at", "2026-11-10T22:00:00Z",
        ])


def test_cli_rejects_api_key_in_provenance_url(tmp_path: Path):
    region = tmp_path / "region.json"
    fuel = tmp_path / "fuel.json"
    out = tmp_path / "report.json"
    region.write_text("[]")
    fuel.write_text("[]")
    with pytest.raises(SystemExit):
        main([
            "--region-json", str(region), "--fuel-json", str(fuel),
            "--output-json", str(out),
            "--region-url", "https://api.eia.gov/v2/test?api_key=SECRET",
            "--fuel-url", "https://api.eia.gov/v2/test",
            "--retrieved-at", "2026-11-10T22:00:00Z",
        ])
    assert not out.exists()
