from multiyear_energy_validation.eia923_monthly_screen import screen_eia923_monthly


def test_generation_is_not_available_power():
    cohort = {"chronology_screened_sites":[{"plant_id":"57373","technology":"solar"}]}
    row = {"plant_id":"57373","year":"2025","month":"07",
           "net_generation_mwh":"1234.5","fuel_code":"SUN",
           "generation_source":"EIA-923","source_sheet":"Page 1","source_row":"42"}
    result = screen_eia923_monthly([row], cohort)
    assert result["sites"][0]["matching_rows"] == 1
    assert result["sites"][0]["reported_net_generation_mwh_by_fuel"][0]["net_generation_mwh"] == 1234.5
    assert not result["sites"][0]["hourly_available_generation_inferred"]
    assert not result["empirical_dispatch_approved"]


def test_reject_missing_provenance_and_nonpositive_generation():
    cohort = {"chronology_screened_sites":[{"plant_id":"57373","technology":"solar"}]}
    base = {"plant_id":"57373","year":"2025","month":"7",
            "net_generation_mwh":"0","fuel_code":"SUN",
            "generation_source":"EIA-923","source_sheet":"Page 1","source_row":"42"}
    result = screen_eia923_monthly([base, {**base,"net_generation_mwh":"10","source_row":""}], cohort)
    assert len(result["rejected"]) == 2
    assert result["sites"][0]["matching_rows"] == 0
