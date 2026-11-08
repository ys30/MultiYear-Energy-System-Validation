import pytest
from multiyear_energy_validation.annual_wind_monthly_alignment import pearson, summarize, MONTHS

def test_pearson():
    assert pearson([1,2,3],[2,4,6])==1
    assert pearson([1,2,3],[6,4,2])==-1
    assert pearson([1,1,1],[2,3,4]) is None

def test_month_length_normalization():
    data={"sites":[{"plant_id":"7526","months":{
        m:{"ws10m_mean_ms":float(i+1),
           "ws10m_mean_cubed_ms3":float((i+1)**3),
           "observed_net_generation_mwh":float((i+1)*d)}
        for i,(m,d) in enumerate(zip(MONTHS,[31,28,31,30,31,30,31,31,30,31,30,31]))}}]}
    result=summarize(data)
    assert result["sites"][0]["monthly_mean_ws10m_vs_daily_normalized_generation_pearson"]==1
    assert not result["weather_to_power_model_validated"]
    assert not result["empirical_dispatch_approved"]

def test_missing_month_rejected():
    with pytest.raises(ValueError,match="months"):
        summarize({"sites":[{"plant_id":"7526","months":{}}]})
