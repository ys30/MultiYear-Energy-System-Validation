from multiyear_energy_validation.annual_wind_first_difference import first_difference_audit
from multiyear_energy_validation.annual_wind_monthly_alignment import MONTHS
import pytest

def test_first_difference_perfect_linear():
    months={m:{"ws10m_mean_ms":float(i+1),
               "ws10m_mean_cubed_ms3":float(i+1),
               "observed_net_generation_mwh":float((i+1)*d)}
            for i,(m,d) in enumerate(zip(MONTHS,(31,28,31,30,31,30,31,31,30,31,30,31)))}
    out=first_difference_audit({"sites":[{"plant_id":"7526","months":months}]})
    assert out["first_difference_pairs"]==11
    assert out["sites"][0]["delta_mean_ws10m_vs_delta_daily_generation_pearson"]==1
    assert not out["not_causal"] is False
    assert not out["empirical_dispatch_approved"]

def test_missing_month_rejected():
    with pytest.raises(ValueError,match="incomplete"):
        first_difference_audit({"sites":[{"plant_id":"7526","months":{}}]})
