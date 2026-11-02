import json
import pytest
from multiyear_energy_validation.schema_audit import (
    summarize_candidate_schema, audit_candidate_file,
)


def test_schema_audit_reports_actual_fields(tmp_path):
    rows = [{"period": "2021-01-01T00", "type": "D",
             "units": "megawatthours", "value": 10, "respondent": "CISO"}]
    report = summarize_candidate_schema(rows)
    assert report["row_count"] == 1
    assert report["categorical_examples"]["units"]["sample_values"] == ["megawatthours"]
    assert "value" in report["field_names"]
    path = tmp_path / "raw.json"
    path.write_text(json.dumps(rows))
    assert audit_candidate_file(path, tmp_path / "report.json")["row_count"] == 1


def test_schema_audit_rejects_empty_or_invalid():
    with pytest.raises(ValueError):
        summarize_candidate_schema([])
    with pytest.raises(ValueError):
        summarize_candidate_schema([1])
