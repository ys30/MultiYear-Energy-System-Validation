"""Offline tests for strict E1.1/E1.2 reconciliation."""
import unittest

from scripts.check_paper_a1_classification_totals import verify


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {
            "source_url": "https://example.org/pinned.parquet",
            "adjacent_year_pairs": [
                {"year_a": 2023, "year_b": 2024,
                 "not_matched_from_a": 2, "not_matched_from_b": 3},
                {"year_a": 2024, "year_b": 2025,
                 "not_matched_from_a": 1, "not_matched_from_b": 2},
            ],
        }
        self.classified = {
            "source_url": "https://example.org/pinned.parquet",
            "classification": [
                {"year_a":2023,"year_b":2024,"side":"only_in_earlier_year",
                 "plant_context":"plant_present_other_year","records":2},
                {"year_a":2023,"year_b":2024,"side":"only_in_later_year",
                 "plant_context":"plant_absent_other_year","records":3},
                {"year_a":2024,"year_b":2025,"side":"only_in_earlier_year",
                 "plant_context":"plant_absent_other_year","records":1},
                {"year_a":2024,"year_b":2025,"side":"only_in_later_year",
                 "plant_context":"plant_present_other_year","records":2},
            ],
        }

    def test_reconciles(self):
        self.assertTrue(verify(self.baseline, self.classified))

    def test_mismatch_fails(self):
        self.classified["classification"][0]["records"] = 1
        with self.assertRaisesRegex(ValueError, "total mismatch"):
            verify(self.baseline, self.classified)

    def test_duplicate_fails(self):
        self.classified["classification"].append(dict(self.classified["classification"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            verify(self.baseline, self.classified)

    def test_provenance_fails(self):
        self.classified["source_url"] = "https://example.org/other.parquet"
        with self.assertRaisesRegex(ValueError, "provenance"):
            verify(self.baseline, self.classified)

    def test_zero_count_category_can_be_omitted(self):
        self.assertTrue(verify(self.baseline, self.classified))


if __name__ == "__main__":
    unittest.main()
