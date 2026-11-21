"""Offline regression tests for the EIA-860M Mesa generator identity probe."""
import io
import sys
import unittest
from pathlib import Path

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_eia860m_mesa_2025 import parse_generator_workbook


def workbook_bytes(records):
    book = Workbook()
    sheet = book.active
    sheet.title = "Operating"
    sheet.append(["Plant Code", "Generator ID", "Nameplate Capacity (MW)", "Status"])
    for plant, gen, capacity, status in records:
        sheet.append([plant, gen, capacity, status])
    buffer = io.BytesIO()
    book.save(buffer)
    book.close()
    return buffer.getvalue()


class MesaMonthlyParserTests(unittest.TestCase):
    def test_exact_plant_and_generator_key_only(self):
        raw = workbook_bytes([
            (50535, "WGNS", 33.6, "(OP) Operating"),
            (50535, "MWD1", 30, "(OP) Operating"),
            (50535, "OTHER", 11, "(OP) Operating"),
            (50536, "WGNS", 27, "(OP) Operating"),
        ])
        _, hits = parse_generator_workbook(raw)
        self.assertEqual({h["generator_id"] for h in hits}, {"WGNS", "MWD1"})
        self.assertEqual({h["generator_id"]: h["fields"]["Nameplate Capacity (MW)"] for h in hits},
                         {"WGNS": "33.6", "MWD1": "30"})

    def test_absent_target_ids_are_not_inferred(self):
        _, hits = parse_generator_workbook(workbook_bytes([(50535, "OTHER", 12, "OP")]))
        self.assertEqual(hits, [])

    def test_unrecognized_workbook_fails_closed(self):
        book = Workbook()
        book.active.append(["Arbitrary", "Headers"])
        output = io.BytesIO()
        book.save(output)
        book.close()
        with self.assertRaisesRegex(ValueError, "No EIA generator sheets recognized"):
            parse_generator_workbook(output.getvalue())


if __name__ == "__main__":
    unittest.main()
