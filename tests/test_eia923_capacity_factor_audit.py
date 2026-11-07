from multiyear_energy_validation.eia923_capacity_factor_audit import audit_monthly_factors, CAPACITY_MW, EXPECTED_FUEL
import pytest


def make_extract():
    return {"year":2025,"month":7,"commissioning_screened_plant_ids":list(CAPACITY_MW),
            "rows":[{"plant_id":pid,"source_sheet":"Page 1 Generation and Fuel Data",
                     "source_row":100+i,"fuel_code":EXPECTED_FUEL[pid],
                     "net_generation_july_mwh":CAPACITY_MW[pid]*744*0.25}
                    for i,pid in enumerate(CAPACITY_MW)]}


def test_capacity_factor_is_descriptive_not_availability():
    result=audit_monthly_factors(make_extract())
    assert len(result["sites"])==5
    assert all(abs(x["monthly_net_capacity_factor"]-0.25)<1e-8 for x in result["sites"])
    assert result["independent_generation_observed"]
    assert not result["hourly_renewable_availability_approved"]
    assert not result["empirical_dispatch_approved"]


def test_reject_duplicate_fuel_rows():
    data=make_extract()
    data["rows"].append(dict(data["rows"][0]))
    with pytest.raises(ValueError,match="ambiguous"):
        audit_monthly_factors(data)


def test_reject_impossible_generation():
    data=make_extract()
    data["rows"][0]["net_generation_july_mwh"]=CAPACITY_MW["57373"]*744*1.1
    with pytest.raises(ValueError,match="bound exceeded"):
        audit_monthly_factors(data)
