from multiyear_energy_validation.physical_conversion_readiness import assess_site, REQUIRED_WEATHER, REQUIRED_PLANT, REQUIRED_VALIDATION


def test_nasa_power_inputs_not_sufficient_for_solar_ac():
    result = assess_site("solar", ("ghi_wm2", "wind_speed_10m_ms"))
    assert not result["physical_conversion_ready"]
    assert {"dni_wm2", "dhi_wm2", "air_temperature_c"} <= set(result["missing_weather_variables"])
    assert "dc_ac_ratio" in result["missing_plant_parameters"]
    assert not result["empirical_dispatch_approved"]


def test_nasa_power_10m_wind_not_hub_height_power():
    result = assess_site("wind", ("wind_speed_10m_ms",))
    assert not result["physical_conversion_ready"]
    assert "surface_pressure_pa" in result["missing_weather_variables"]
    assert "hub_height_m" in result["missing_plant_parameters"]
    assert "turbine_power_curve" in result["missing_plant_parameters"]


def test_only_fully_documented_candidate_is_input_ready_not_dispatch_approved():
    result = assess_site("solar", REQUIRED_WEATHER["solar"],
                         {k: "documented" for k in REQUIRED_PLANT["solar"]},
                         {k: "documented" for k in REQUIRED_VALIDATION})
    assert result["physical_conversion_ready"]
    assert not result["empirical_dispatch_approved"]
