import pytest
from multiyear_energy_validation.paper_eia930_coverage_contract import audit_eia930_coverage_reports

def sample():
    return {year:{"year":year,"expected_hours":hours,"unique_hours":hours,
                  "valid_hours":hours,"missing_hours":0,"duplicate_rows":0,
                  "invalid_timestamps":0,"outside_year":0,"invalid_values":0,
                  "complete":True}
            for year,hours in ((2024,8784),(2025,8760))}

def test_leap_year_and_ordinary_year_denominators():
    result=audit_eia930_coverage_reports(sample())
    assert [r["expected_hours"] for r in result["demand_coverage"]]==[8784,8760]
    assert result["fuel_series_completeness_not_inferred"]
    assert not result["empirical_dispatch_approved"]

def test_reject_wrong_denominator():
    reports=sample()
    reports[2024]["expected_hours"]=8760
    with pytest.raises(ValueError,match="calendar-hour"):
        audit_eia930_coverage_reports(reports)

def test_reject_duplicate_hours():
    reports=sample()
    reports[2025]["duplicate_rows"]=1
    with pytest.raises(ValueError,match="quality flags"):
        audit_eia930_coverage_reports(reports)

def test_reject_incomplete_demand():
    reports=sample()
    reports[2025]["valid_hours"]=8759
    reports[2025]["complete"]=False
    with pytest.raises(ValueError,match="incomplete"):
        audit_eia930_coverage_reports(reports)

def test_reject_missing_year():
    with pytest.raises(ValueError,match="two independently"):
        audit_eia930_coverage_reports({2025:sample()[2025]})
