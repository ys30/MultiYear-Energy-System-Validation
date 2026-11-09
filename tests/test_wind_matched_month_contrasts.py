"""Regression tests for matched-month interannual contrasts."""
import calendar
import pytest
from multiyear_energy_validation.annual_wind_monthly_alignment import MONTHS
from multiyear_energy_validation.wind_matched_month_contrasts import audit

def fixtures():
    reports={}
    for year in (2024,2025):
        sites=[]
        for pid in ("57484","57514","7526"):
            months={}
            for i,m in enumerate(MONTHS):
                days=calendar.monthrange(year,i+1)[1]
                ws=float(i+1)+(0.2*(i+1) if year==2025 else 0)
                daily=10+2*(i+1)+(0.4*(i+1) if year==2025 else 0)
                months[m]={"ws10m_mean_ms":ws,
                           "observed_net_generation_mwh":daily*days}
            sites.append({"plant_id":pid,"months":months})
        reports[year]={"year":year,"sites":sites}
    return reports

def test_same_month_interannual_contrasts_and_leap_year():
    out=audit(fixtures())
    assert len(out["sites"])==3
    for s in out["sites"]:
        assert s["matched_month_year_difference_pearson_r"]==1
        assert len(s["monthly_contrasts"])==12
        assert s["monthly_contrasts"][1]["month"]=="february"
        assert s["monthly_contrasts"][1]["delta_daily_generation_2025_minus_2024_mwh_per_day"]==0.8
    assert out["only_two_years"]
    assert not out["empirical_dispatch_approved"]

def test_year_mismatch_rejected():
    reports=fixtures()
    reports[2024]["year"]=2025
    with pytest.raises(ValueError,match="year mismatch"):
        audit(reports)
