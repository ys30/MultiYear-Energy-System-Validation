"""Regression tests for historical EIA-860 annual transition evidence."""
import copy
import unittest

from scripts.report_official_eia860_historical_transitions import build_report


class HistoricalTransitionsTests(unittest.TestCase):
    def setUp(self):
        self.audit = {"historical_four_plant_records": []}
        for year in (2023, 2024):
            for plant, generator in [(50535, "WGNS"), (61446, "PV2"), (63094, "SBAD1"),
                                     (63094, "SBAD2"), (65820, "OWS")]:
                self.audit["historical_four_plant_records"].append({
                    "year": year, "plant_id_eia": plant, "generator_id": generator,
                    "sheet": "Operable", "fields": {
                        "Status": "OP", "Nameplate Capacity (MW)": "10",
                        "Operating Year": "2022", "Operating Month": "6"}})

    def test_stable_cohort(self):
        result = build_report(self.audit)
        self.assertEqual(result["historical_generator_keys"], 5)
        self.assertEqual(result["changed_generator_keys"], 0)
        self.assertFalse(result["generator_identity_crosswalk_verified"])

    def test_detect_status_and_capacity_change(self):
        row = self.audit["historical_four_plant_records"][0]
        row["fields"]["Status"] = "RE"
        row["fields"]["Nameplate Capacity (MW)"] = "27"
        result = build_report(self.audit)
        self.assertEqual(result["changed_generator_keys"], 1)
        self.assertIn("Status", result["records"][0]["changed_fields"])
        self.assertIn("Nameplate Capacity (MW)", result["records"][0]["changed_fields"])

    def test_duplicate_fails_closed(self):
        self.audit["historical_four_plant_records"].append(
            copy.deepcopy(self.audit["historical_four_plant_records"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build_report(self.audit)

    def test_missing_year_fails_closed(self):
        self.audit["historical_four_plant_records"].pop()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            build_report(self.audit)

    def test_missing_required_field_fails_closed(self):
        self.audit["historical_four_plant_records"][0]["fields"].pop("Status")
        with self.assertRaisesRegex(ValueError, "Missing required"):
            build_report(self.audit)


if __name__ == "__main__":
    unittest.main()
