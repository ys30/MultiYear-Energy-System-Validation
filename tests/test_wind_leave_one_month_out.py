"""Deterministic tests of wind leave-one-month-out sensitivity."""
import calendar
from multiyear_energy_validation.annual_wind_monthly_alignment import MONTHS
from multiyear_energy_validation.wind_leave_one_month_out import audit

def reports():
    out={}
    for year in (2024,2025):
        months={}
        for i,m in enumerate(MONTHS):
            days=calendar.monthrange(year,i+1)[1]
            months[m]={"ws10m_mean_ms":float(i+1),
                       "observed_net_generation_mwh":float((i+1)*days)}
        out[year]={"year":year,"sites":[{"plant_id":p,"months":months}
                  for p in ("57484","57514","7526")]}
    return out

def test_leave_one_month_out_perfect_alignment_and_leap_year():
    result=audit(reports())
    assert len(result["sites"])==6
    for site in result["sites"]:
        assert site["full_12_month_r"]==1
        assert site["leave_one_month_out_min_r"]==1
        assert site["leave_one_month_out_max_r"]==1
        assert site["largest_absolute_r_change"]==0
        assert len(site["leave_one_month_out"])==12
        assert {v["excluded_month"] for v in site["leave_one_month_out"]}==set(MONTHS)
    assert result["not_out_of_sample_forecast"]

def test_rejects_incomplete_months():
    data=reports()
    del data[2024]["sites"][0]["months"]["february"]
    try:
        audit(data)
    except ValueError as exc:
        assert "incomplete" in str(exc)
    else:
        raise AssertionError("incomplete months accepted")
