import pytest
from multiyear_energy_validation.paper_demand_two_year import merge_demand_coverage

def reports():
    return {y:{"year":y,"expected_hours":h,"valid_demand_hours":h,
               "demand_coverage_fraction":1.0,"anomaly_free_not_inferred":True,
               "fuel_series_completeness_not_inferred":True,
               "empirical_dispatch_approved":False}
            for y,h in ((2024,8784),(2025,8760))}

def test_merge_years_without_promoting_dispatch():
    result=merge_demand_coverage(reports())
    assert result["valid_demand_hours_total"]==17544
    assert result["fuel_coverage_not_inferred"]
    assert not result["empirical_dispatch_approved"]

def test_missing_year_fails_closed():
    with pytest.raises(ValueError,match="both 2024"):
        merge_demand_coverage({2025:reports()[2025]})

def test_mismatched_hours_fails_closed():
    data=reports()
    data[2024]["valid_demand_hours"]=8760
    with pytest.raises(ValueError,match="coverage"):
        merge_demand_coverage(data)

def test_missing_caveat_fails_closed():
    data=reports()
    data[2025]["anomaly_free_not_inferred"]=False
    with pytest.raises(ValueError,match="caveats"):
        merge_demand_coverage(data)
