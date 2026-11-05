from multiyear_energy_validation.plant_weather_mapping_gate import audit_plant_capacity


def plant(**updates):
    row = {"plant_id": "1", "generator_id": "A", "latitude": 36.5,
           "longitude": -119.5, "capacity_mw": 80, "technology": "solar",
           "report_year": 2025, "operating_status": "OP",
           "ciso_membership_verified": True}
    row.update(updates)
    return row


def test_operational_plant_passes_schema_only():
    result = audit_plant_capacity([plant()], 2025)
    assert result["accepted_count"] == 1
    assert result["accepted_capacity_mw"] == 80
    assert not result["dispatch_approved"]


def test_geography_does_not_prove_ciso_membership():
    result = audit_plant_capacity([plant(ciso_membership_verified=False)], 2025)
    assert result["accepted_count"] == 0
    assert "ciso_membership_not_verified" in result["rejected"][0]["reasons"]


def test_duplicate_and_retired_rejected():
    result = audit_plant_capacity([plant(), plant(operating_status="RE")], 2025)
    assert result["rejected_count"] == 1
    assert "duplicate_generator" in result["rejected"][0]["reasons"]
