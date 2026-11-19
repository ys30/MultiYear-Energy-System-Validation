"""Enforce explicit unresolved historical generator identity decisions."""
import csv
from pathlib import Path


def test_historical_crosswalk_is_not_inferred():
    path = Path("data/pudl/project_a_historical_identity_review.csv")
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert {r["plant_id_eia"] for r in rows} == {"50535", "61446", "63094", "65820"}
    for r in rows:
        assert r["official_historical_rows_verified"] == "true"
        assert r["exact_id_overlap"] == "false"
        assert r["physical_identity_crosswalk_verified"] == "false"
        assert r["physical_commissioning_verified"] == "false"
        assert r["empirical_dispatch_approved"] == "false"
        assert r["review_status"] == "requires_independent_evidence"
        assert set(r["historical_generator_ids_2023_2024"].split("|")).isdisjoint(
            r["target_generator_ids_2025"].split("|"))
