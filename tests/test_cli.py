import csv
from datetime import datetime, timedelta, timezone

import pytest
from multiyear_energy_validation.cli import main


def test_cli_requires_source_semantic_confirmation(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("utc,mw\\n", encoding="utf-8")
    with pytest.raises(SystemExit) as err:
        main(["--csv", str(p), "--output-dir", str(tmp_path / "out"),
              "--year", "2021", "--timestamp-column", "utc",
              "--demand-column", "mw", "--source-uri", "fixture",
              "--retrieved-at", "2026-11-02T00:00:00Z"])
    assert err.value.code == 2


def test_cli_writes_complete_report(tmp_path, capsys):
    p = tmp_path / "x.csv"
    start = datetime(2021, 1, 1, tzinfo=timezone.utc)
    with p.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["utc", "mw"])
        for i in range(8760):
            writer.writerow([(start + timedelta(hours=i)).isoformat(), 5])
    result = main(["--csv", str(p), "--output-dir", str(tmp_path / "out"),
                   "--year", "2021", "--timestamp-column", "utc",
                   "--demand-column", "mw", "--source-uri", "synthetic-fixture",
                   "--retrieved-at", "2026-11-02T00:00:00Z",
                   "--confirm-utc-interval-start", "--confirm-observed-demand-mw"])
    assert result == 0
    assert (tmp_path / "out" / "all_2021_table1.csv").exists()
    assert '"complete": true' in capsys.readouterr().out
