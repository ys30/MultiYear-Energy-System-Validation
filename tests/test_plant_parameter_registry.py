from multiyear_energy_validation.plant_parameter_registry import build_registry


def test_unknown_parameters_are_not_imputed():
    audit = {"sites": [
        {"plant_id":"1","group":"solar","pv_only_technology":True,
         "wind_only_technology":False,"total_nameplate_mw":100,
         "generator_count":2,"eia_technology_nameplate_mw":{"Solar Photovoltaic":100}},
        {"plant_id":"2","group":"wind","pv_only_technology":False,
         "wind_only_technology":True,"total_nameplate_mw":80,
         "generator_count":1,"eia_technology_nameplate_mw":{"Onshore Wind Turbine":80}},
    ]}
    result = build_registry(audit)
    assert len(result["sites"]) == 2
    assert all(p["value"] is None and p["status"] == "unknown"
               for site in result["sites"] for p in site["engineering_parameters"].values())
    assert not result["empirical_dispatch_approved"]


def test_solar_thermal_rejected_from_pv_registry():
    import pytest
    with pytest.raises(ValueError):
        build_registry({"sites":[
            {"plant_id":"3","group":"solar","pv_only_technology":False,
             "wind_only_technology":False,"total_nameplate_mw":10,
             "generator_count":1,"eia_technology_nameplate_mw":{"Solar Thermal":10}}
        ]})
