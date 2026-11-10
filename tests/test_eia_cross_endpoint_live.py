"""Offline end-to-end tests for the live EIA cross-endpoint workflow."""
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from urllib.error import HTTPError, URLError

from multiyear_energy_validation import eia_cross_endpoint_live as live


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.payload


def test_live_audit_provenance_and_no_api_key_leak(monkeypatch, tmp_path: Path, capsys):
    monkeypatch.setenv("EIA_API_KEY", "SUPER_SECRET_KEY")
    periods = [f"2025-07-31T{hour:02d}" for hour in range(19, 24)]
    ng = [29677, 29776, 27732, 30783, 31641]
    fuel_totals = [29677, 29775, 30003, 30783, 31642]
    requests = []

    def fake_urlopen(request, timeout):
        url = request.full_url
        requests.append(url)
        assert parse_qs(urlsplit(url).query)["api_key"] == ["SUPER_SECRET_KEY"]
        if "/region-data/" in url:
            rows = [
                {"period": p, "respondent": "CISO", "type": "NG",
                 "value": str(v), "value-units": "megawatthours"}
                for p, v in zip(periods, ng)
            ]
        else:
            rows = [
                row for p, v in zip(periods, fuel_totals)
                for row in (
                    {"period": p, "respondent": "CISO", "fueltype": "OTH",
                     "value": "-10", "value-units": "megawatthours"},
                    {"period": p, "respondent": "CISO", "fueltype": "OTHER",
                     "value": str(v + 10), "value-units": "megawatthours"},
                )
            ]
        return FakeResponse(json.dumps({"response": {"total": len(rows), "data": rows}}).encode())

    monkeypatch.setattr(live, "urlopen", fake_urlopen)
    out = tmp_path / "audit"
    assert live.main(["--output-dir", str(out)]) == 0
    report = json.loads((out / "cross_endpoint_audit.json").read_text())
    assert [r["fuel_minus_region_mwh"] for r in report["rows"]] == [
        "0", "-1", "2271", "0", "1"
    ]
    assert report["rows"][2]["fuel_values_mwh"]["OTH"] == "-10"
    assert not report["empirical_dispatch_approved"]
    assert len(requests) == 2
    assert report["source"]["region"]["sha256"] == hashlib.sha256(
        (out / "region_raw.json").read_bytes()
    ).hexdigest()
    assert "SUPER_SECRET_KEY" not in capsys.readouterr().out
    for file in out.iterdir():
        assert "SUPER_SECRET_KEY" not in file.read_text()


def test_live_audit_rejects_partial_periods(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("EIA_API_KEY", "TEST_SECRET")

    def fake_urlopen(request, timeout):
        row = {
            "period": "2025-07-31T21", "respondent": "CISO",
            "value": "100", "value-units": "megawatthours",
        }
        if "/region-data/" in request.full_url:
            row["type"] = "NG"
        else:
            row["fueltype"] = "OTH"
        return FakeResponse(json.dumps({"response": {"total": 1, "data": [row]}}).encode())

    monkeypatch.setattr(live, "urlopen", fake_urlopen)
    with pytest.raises(ValueError, match="Five-hour period coverage incomplete"):
        live.main(["--output-dir", str(tmp_path / "audit")])
    assert not (tmp_path / "audit" / "cross_endpoint_audit.json").exists()
    assert not (tmp_path / "audit" / "region_raw.json").exists()
    assert not (tmp_path / "audit" / "fuel_raw.json").exists()


def test_http_error_never_exposes_secret_in_exception(monkeypatch):
    monkeypatch.setenv("EIA_API_KEY", "DO_NOT_LEAK_SECRET")

    def failing_urlopen(request, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(live, "urlopen", failing_urlopen)
    with pytest.raises(RuntimeError, match="HTTP status 403") as caught:
        live._fetch("region-data/", "DO_NOT_LEAK_SECRET", kind="NG")
    assert "DO_NOT_LEAK_SECRET" not in str(caught.value)
    assert caught.value.__cause__ is None


def test_network_error_never_exposes_secret_in_exception(monkeypatch):
    def failing_urlopen(request, timeout):
        raise URLError("network request failed: " + request.full_url)

    monkeypatch.setattr(live, "urlopen", failing_urlopen)
    with pytest.raises(RuntimeError, match="network error") as caught:
        live._fetch("fuel-type-data/", "DO_NOT_LEAK_SECRET")
    assert "DO_NOT_LEAK_SECRET" not in str(caught.value)
    assert caught.value.__cause__ is None
