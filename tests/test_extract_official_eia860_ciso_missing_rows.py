"""Synthetic workbook regression: malformed CISO generator rows must not disappear."""
import importlib.util
import io
import zipfile
from pathlib import Path

import pytest
from openpyxl import Workbook

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "extract_official_eia860_ciso.py"
spec = importlib.util.spec_from_file_location("extract_ciso", SCRIPT)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


def workbook_bytes(headers, rows):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    data = io.BytesIO()
    wb.save(data)
    return data.getvalue()


@pytest.mark.parametrize("generator_id,status,match", [
    (None, "OP", "Missing CISO generator ID"),
    ("G1", None, "Missing CISO generator status"),
])
def test_ciso_missing_fields_fail_closed(tmp_path, generator_id, status, match):
    archive = tmp_path / "eia8602025.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("2___Plant_Y2025.xlsx", workbook_bytes(
            ["Plant Code", "Balancing Authority Code"], [[6100, "CISO"]]))
        z.writestr("3_1_Generator_Y2025.xlsx", workbook_bytes(
            ["Plant Code", "Generator ID", "Status", "Nameplate Capacity (MW)"],
            [[6100, generator_id, status, 351]]))
    with pytest.raises(ValueError, match=match):
        extractor.extract(archive, 2025, tmp_path / "out")
    assert not (tmp_path / "out" / "eia860_ciso_generators_2025.csv").exists()
