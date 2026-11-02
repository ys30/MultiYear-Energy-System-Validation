import hashlib
import json

import pytest
from multiyear_energy_validation import eia_snapshot


def test_snapshot_preserves_provenance_without_key(tmp_path, monkeypatch):
    monkeypatch.setattr(eia_snapshot, "fetch_candidate_pages",
        lambda **kwargs: [{"period": "2021-01-01T00", "value": "100"}])
    manifest = eia_snapshot.save_candidate_snapshot(
        tmp_path, api_key="SECRET_KEY", respondent="CISO",
        start="2021-01-01T00", end="2021-01-01T00",
        retrieved_at="2026-11-02T18:00:00Z",
    )
    raw = (tmp_path / "eia930_candidate_rows.json").read_bytes()
    assert manifest["raw_sha256"] == hashlib.sha256(raw).hexdigest()
    assert manifest["row_count"] == 1
    assert "SECRET_KEY" not in (tmp_path / "manifest.json").read_text()
    assert manifest["schema_verified"] is False


def test_empty_response_does_not_write(tmp_path, monkeypatch):
    monkeypatch.setattr(eia_snapshot, "fetch_candidate_pages",
        lambda **kwargs: [])
    with pytest.raises(ValueError, match="empty"):
        eia_snapshot.save_candidate_snapshot(
            tmp_path, api_key="KEY", respondent="CISO",
            start="2021", end="2021", retrieved_at="2026-11-02T18:00:00Z",
        )
    assert not (tmp_path / "manifest.json").exists()
