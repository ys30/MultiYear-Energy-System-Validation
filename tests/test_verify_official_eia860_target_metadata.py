"""Synthetic tests of fail-closed official annual generator metadata gate."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_official_eia860_target_metadata import verify


class OfficialMetadataGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.targets = Path(self.temp.name) / "targets.csv"
        with self.targets.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=[
                "plant_id_eia", "generator_id", "reported_operating_year",
                "status_2025", "op_nameplate_mw_2025"])
            writer.writeheader()
            for i in range(29):
                writer.writerow({"plant_id_eia": 1000+i, "generator_id": f"G{i}",
                                 "reported_operating_year": 2024,
                                 "status_2025": "OP", "op_nameplate_mw_2025": 10.0})
        self.official = {"target_year_records": [
            {"year": 2025, "plant_id_eia": 1000+i, "generator_id": f"G{i}",
             "exact_match": True, "official_selected_metadata": [{
                 "sheet": "Operable", "row": i+3, "fields": {
                     "Operating Year": "2024", "Status": "OP",
                     "Nameplate Capacity (MW)": "10"}}]}
            for i in range(29)]}

    def test_matching_metadata_passes(self):
        result = verify(self.official, self.targets)
        self.assertEqual(result["metadata_mismatches"], 0)
        self.assertFalse(result["empirical_dispatch_approved"])

    def test_operating_year_mismatch_fails(self):
        self.official["target_year_records"][0]["official_selected_metadata"][0]["fields"]["Operating Year"] = "2023"
        with self.assertRaisesRegex(ValueError, "Operating Year"):
            verify(self.official, self.targets)

    def test_capacity_mismatch_fails(self):
        self.official["target_year_records"][0]["official_selected_metadata"][0]["fields"]["Nameplate Capacity (MW)"] = "11"
        with self.assertRaisesRegex(ValueError, "Nameplate Capacity"):
            verify(self.official, self.targets)

    def test_duplicate_official_row_fails(self):
        record = self.official["target_year_records"][0]
        record["official_selected_metadata"].append(record["official_selected_metadata"][0].copy())
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            verify(self.official, self.targets)

    def test_missing_exact_key_fails(self):
        self.official["target_year_records"][0]["exact_match"] = False
        with self.assertRaisesRegex(ValueError, "missing"):
            verify(self.official, self.targets)


if __name__ == "__main__":
    unittest.main()
