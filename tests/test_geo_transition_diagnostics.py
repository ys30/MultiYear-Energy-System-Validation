from multiyear_energy_validation.geo_transition_diagnostics import adjacent_transition


def test_geo_other_transition_not_proven_reclassification():
    before = {"period": "2025-12-16T08", "geo_reported": False,
              "geo_mwh": None, "other_mwh": 143, "fuel_sum_mwh": 13281}
    after = {"period": "2025-12-16T09", "geo_reported": True,
             "geo_mwh": 729, "other_mwh": -368, "fuel_sum_mwh": 11901}
    result = adjacent_transition(before, after)
    assert result["other_change_mwh"] == -511
    assert result["geo_plus_other_change_mwh"] == 218
    assert result["total_generation_change_mwh"] == -1380
    assert not result["reclassification_proven"]
