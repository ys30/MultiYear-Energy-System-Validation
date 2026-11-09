"""Regression guards for independent-year comparison and leap-day normalization."""
import calendar
from multiyear_energy_validation.annual_wind_monthly_alignment import MONTHS,summarize
from multiyear_energy_validation.annual_wind_first_difference import first_difference_audit
from multiyear_energy_validation.wind_2024_2025_comparison import compare

def sample(year):
    months={}
    for i,m in enumerate(MONTHS):
        days=calendar.monthrange(year,i+1)[1]
        months[m]={"ws10m_mean_ms":float((i+1)**2),
                   "ws10m_mean_cubed_ms3":float((i+1)**3),
                   "observed_net_generation_mwh":float((i+1)**2*days)}
    return {"year":year,"sites":[{"plant_id":p,"months":months} for p in ("57484","57514","7526")]}

def test_leap_day_normalization_preserves_raw_generation():
    report=sample(2024)
    original=report["sites"][0]["months"]["february"]["observed_net_generation_mwh"]
    assert original==116.0
    level=summarize(report)
    diff=first_difference_audit(report)
    assert level["sites"][0]["monthly_mean_ws10m_vs_daily_normalized_generation_pearson"]==1
    assert diff["sites"][0]["delta_mean_ws10m_vs_delta_daily_generation_pearson"]==1
    assert report["sites"][0]["months"]["february"]["observed_net_generation_mwh"]==original
    assert "2024" in diff["source"]

def test_comparison_years_and_cohort():
    r24=sample(2024);r25=sample(2025)
    rep={"year":2024,"level":summarize(r24),"first_difference":first_difference_audit(r24)}
    out=compare(rep,summarize(r25),first_difference_audit(r25))
    assert out["years"]==[2024,2025]
    assert len(out["sites"])==3
    assert all(s["metrics"]["monthly_mean_ws10m_vs_daily_normalized_generation_pearson"]["delta_2025_minus_2024"]==0 for s in out["sites"])
    assert not out["empirical_dispatch_approved"]
