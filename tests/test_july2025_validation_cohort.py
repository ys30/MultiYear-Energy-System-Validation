from multiyear_energy_validation.july2025_validation_cohort import select_commissioned_sites


def test_post_window_site_excluded_without_deleting_weather():
    rows = [
        {"plant_id":"57695","technology":"solar",
         "all_2025_op_generators_commissioned_by_2025_07":True,
         "nameplate_mw_by_chronology_status":{"commissioned_by_pilot_month_per_eia860":585.9}},
        {"plant_id":"64210","technology":"solar",
         "all_2025_op_generators_commissioned_by_2025_07":False,
         "nameplate_mw_by_chronology_status":{"commissioned_after_pilot_month":500}},
    ]
    result = select_commissioned_sites({"sites":rows})
    assert [x["plant_id"] for x in result["chronology_screened_sites"]] == ["57695"]
    assert [x["plant_id"] for x in result["excluded_from_july_operating_validation"]] == ["64210"]
    assert not result["independent_generation_verified"]
    assert not result["empirical_dispatch_approved"]
