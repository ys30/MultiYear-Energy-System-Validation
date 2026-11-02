import json

import pytest
from multiyear_energy_validation import download_cli


def test_requires_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(SystemExit) as err:
        download_cli.main(["--respondent", "CISO", "--start", "2021-01-01T00",
            "--end", "2021-01-01T23", "--output-dir", str(tmp_path)])
    assert err.value.code == 2


def test_uses_environment_key_without_printing_it(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("EIA_API_KEY", "PRIVATE_TEST_KEY")
    def fake_snapshot(output_dir, **kwargs):
        assert kwargs["api_key"] == "PRIVATE_TEST_KEY"
        return {"row_count": 24, "status": "unverified_candidate_not_for_empirical_results"}
    monkeypatch.setattr(download_cli, "save_candidate_snapshot", fake_snapshot)
    assert download_cli.main(["--respondent", "CISO", "--start", "2021-01-01T00",
        "--end", "2021-01-01T23", "--output-dir", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "PRIVATE_TEST_KEY" not in output
    assert json.loads(output)["row_count"] == 24
