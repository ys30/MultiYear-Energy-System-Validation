"""Synthetic fixtures for official EIA-860 workbook schema detection."""
import io
import json
import zipfile

from openpyxl import Workbook

from scripts.audit_official_eia860_workbooks import inspect_archive


def workbook_bytes(headers):
    book = Workbook()
    sheet = book.active
    sheet.title = "Operating"
    sheet.append(["EIA Form 860", None, None, None])
    sheet.append(headers)
    sheet.append([1] * len(headers))
    stream = io.BytesIO()
    book.save(stream)
    return stream.getvalue()


def test_detects_plant_and_generator_headers(tmp_path):
    path = tmp_path / "official.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("2___Plant_2025.xlsx",
                         workbook_bytes(["Plant Code", "Balancing Authority Code"]))
        archive.writestr("3_1_Generator_2025.xlsx",
                         workbook_bytes(["Plant Code", "Generator ID", "Nameplate Capacity (MW)"]))
    report = inspect_archive(path)
    assert report["ready_for_manual_schema_review"] is True
    assert len(report["candidates"]) == 2
    assert report["fleet_validated"] is False
    assert report["ba_mapping_validated"] is False


def test_rejects_missing_generator_columns(tmp_path):
    path = tmp_path / "incomplete.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("2___Plant_2025.xlsx",
                         workbook_bytes(["Plant Code", "Balancing Authority Code"]))
        archive.writestr("3_1_Generator_2025.xlsx",
                         workbook_bytes(["Plant Code", "Capacity (MW)"]))
    report = inspect_archive(path)
    assert report["ready_for_manual_schema_review"] is False
    assert {x["kind"] for x in report["candidates"]} == {"plant"}
