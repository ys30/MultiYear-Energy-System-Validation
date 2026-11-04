"""Contract tests for EIA component API response handling."""
import io
import json
from unittest.mock import patch

import pytest

from multiyear_energy_validation.eia_component_audit import fetch_component


class Response(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.close()


def mock_response(rows, total=None):
    body = {"response": {"total": len(rows) if total is None else total, "data": rows}}
    return Response(json.dumps(body).encode())


def test_component_accepts_complete_matching_rows():
    rows = [{"period": "2025-07-31T21", "respondent": "CISO",
             "type": "NG", "value": "25000", "value-units": "megawatthours"}]
    with patch("multiyear_energy_validation.eia_component_audit.urlopen",
               return_value=mock_response(rows)):
        result = fetch_component(api_key="test", kind="NG")
    assert result["total"] == 1
    assert result["rows"][0]["value"] == "25000"


def test_component_rejects_truncated_response():
    rows = [{"respondent": "CISO", "type": "D"}]
    with patch("multiyear_energy_validation.eia_component_audit.urlopen",
               return_value=mock_response(rows, total=2)):
        with pytest.raises(ValueError, match="row count"):
            fetch_component(api_key="test", kind="D")


def test_component_rejects_wrong_type():
    rows = [{"respondent": "CISO", "type": "D"}]
    with patch("multiyear_energy_validation.eia_component_audit.urlopen",
               return_value=mock_response(rows)):
        with pytest.raises(ValueError, match="facet mismatch"):
            fetch_component(api_key="test", kind="TI")


def test_component_rejects_unknown_type():
    with pytest.raises(ValueError, match="unsupported"):
        fetch_component(api_key="test", kind="UNKNOWN")
