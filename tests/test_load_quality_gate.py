import pytest

from multiyear_energy_validation.load_quality_gate import (
    ANOMALY_HOUR_UTC, classify_load_hour, decide_dispatch_gate,
)


def test_flagged_source_is_not_approved_even_with_scenario():
    item = classify_load_hour(ANOMALY_HOUR_UTC, 11819, scenario_value=29883.5)
    assert item.source_observation_mwh == 11819
    assert item.scenario_observation_mwh == 29883.5
    assert not item.empirical_approved
    gate = decide_dispatch_gate(
        [item], renewable_availability=True, thermal_costs=True,
        storage_parameters=True, interchange_boundaries=True,
    )
    assert not gate["r02_empirical_dispatch_approved"]
    assert gate["unresolved_load_hours"] == [ANOMALY_HOUR_UTC]


def test_unflagged_hour_still_requires_all_inputs():
    item = classify_load_hour("2025-07-31T19:00:00+00:00", 29881)
    gate = decide_dispatch_gate([item])
    assert not gate["r02_empirical_dispatch_approved"]
    assert len(gate["missing_inputs"]) == 4


def test_unflagged_hour_cannot_be_replaced():
    with pytest.raises(ValueError, match="flagged"):
        classify_load_hour("2025-07-31T19:00:00+00:00", 29881, scenario_value=30000)


def test_empty_input_never_approves_dispatch():
    gate = decide_dispatch_gate(
        [], renewable_availability=True, thermal_costs=True,
        storage_parameters=True, interchange_boundaries=True,
    )
    assert not gate["r02_empirical_dispatch_approved"]
