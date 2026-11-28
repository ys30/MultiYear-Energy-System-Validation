"""Offline tests for Paper A1 national exact-key continuity logic."""
import unittest

from scripts.paper_a1_national_baseline import analyze


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, counts, pairs, duplicates=None):
        self.counts = counts
        self.pairs = pairs
        self.duplicates = duplicates or []
        self.sql = []

    def execute(self, sql):
        self.sql.append(sql)
        if "HAVING count(*) > 1" in sql:
            return FakeResult(self.duplicates)
        if "null_keys" in sql:
            return FakeResult(self.counts)
        if "exact_key_overlap" in sql:
            return FakeResult(self.pairs)
        return FakeResult([])


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.counts = [(2023, 100, 20, 0), (2024, 110, 22, 0), (2025, 120, 24, 0)]
        self.pairs = [(2023, 2024, 100, 110, 90), (2024, 2025, 110, 120, 95)]

    def test_exact_overlap_and_nonmatch_are_descriptive(self):
        result = analyze(FakeConnection(self.counts, self.pairs))
        self.assertEqual(result["adjacent_year_pairs"][0]["not_matched_from_a"], 10)
        self.assertEqual(result["adjacent_year_pairs"][0]["not_matched_from_b"], 20)
        self.assertFalse(result["empirical_dispatch_approved"])

    def test_duplicate_keys_fail(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            analyze(FakeConnection(self.counts, self.pairs, [(2024, "1", "A", 2)]))

    def test_missing_year_fails(self):
        with self.assertRaisesRegex(ValueError, "three expected years"):
            analyze(FakeConnection(self.counts[:2], self.pairs))

    def test_missing_overlap_pair_fails(self):
        with self.assertRaisesRegex(ValueError, "Missing adjacent-year"):
            analyze(FakeConnection(self.counts, self.pairs[:1]))

    def test_inconsistent_denominator_fails(self):
        bad_pairs = [(2023, 2024, 99, 110, 90), self.pairs[1]]
        with self.assertRaisesRegex(ValueError, "denominator"):
            analyze(FakeConnection(self.counts, bad_pairs))

    def test_impossible_overlap_fails(self):
        bad_pairs = [(2023, 2024, 100, 110, 101), self.pairs[1]]
        with self.assertRaisesRegex(ValueError, "Impossible"):
            analyze(FakeConnection(self.counts, bad_pairs))

    def test_null_keys_fail(self):
        counts = [(2023, 100, 20, 1), *self.counts[1:]]
        with self.assertRaisesRegex(ValueError, "Missing exact generator keys"):
            analyze(FakeConnection(counts, self.pairs))


if __name__ == "__main__":
    unittest.main()
