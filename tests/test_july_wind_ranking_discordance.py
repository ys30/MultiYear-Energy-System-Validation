from multiyear_energy_validation.july_wind_ranking_discordance import audit_ranking
import pytest


def test_rank_discordance_not_causal():
    data={"sites":[
        {"plant_id":"57484","nasa_power_ws10m_mean_ms":2.74,"observed_july_net_capacity_factor":.4083},
        {"plant_id":"57514","nasa_power_ws10m_mean_ms":5.69,"observed_july_net_capacity_factor":.2316},
        {"plant_id":"7526","nasa_power_ws10m_mean_ms":5.63,"observed_july_net_capacity_factor":.5816},
    ]}
    report=audit_ranking(data)
    assert report["opposite_rank_order_pair_count"]==2
    assert report["solano_vs_57514_abs_cf_difference_percentage_points"]==35.0
    assert report["ranking_is_not_causal_attribution"]
    assert not report["empirical_dispatch_approved"]


def test_reject_wrong_cohort():
    with pytest.raises(ValueError,match="cohort"):
        audit_ranking({"sites":[]})
