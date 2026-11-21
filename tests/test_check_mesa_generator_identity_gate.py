"""Synthetic contract tests for the Mesa generator identity gate."""
import unittest

from scripts.check_mesa_generator_identity_gate import evaluate


class MesaIdentityGateTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "plant_id_eia": 50535,
            "historical_generator_id": "WGNS",
            "target_generator_id": "MWD1",
            "identity_evidence_type": "monthly_status_transition",
            "source_url": "https://www.eia.gov/",
            "source_document_sha256": "a" * 64,
            "independent_review_status": "pending",
        }

    def test_monthly_status_does_not_prove_identity(self):
        self.assertFalse(evaluate(self.evidence)["identity_crosswalk_verified"])

    def test_missing_primary_source_fails(self):
        self.evidence["identity_evidence_type"] = "primary_generator_lineage"
        self.evidence["source_document_sha256"] = ""
        self.assertFalse(evaluate(self.evidence)["identity_crosswalk_verified"])

    def test_unreviewed_lineage_fails(self):
        self.evidence["identity_evidence_type"] = "primary_generator_lineage"
        self.assertFalse(evaluate(self.evidence)["identity_crosswalk_verified"])

    def test_reviewed_lineage_still_does_not_approve_dispatch(self):
        self.evidence.update(identity_evidence_type="primary_generator_lineage",
                             independent_review_status="approved")
        result = evaluate(self.evidence)
        self.assertTrue(result["identity_crosswalk_verified"])
        self.assertFalse(result["empirical_dispatch_approved"])

    def test_wrong_plant_fails(self):
        self.evidence["plant_id_eia"] = 50536
        with self.assertRaisesRegex(ValueError, "plant ID"):
            evaluate(self.evidence)


if __name__ == "__main__":
    unittest.main()
