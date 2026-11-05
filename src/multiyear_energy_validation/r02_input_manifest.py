"""R02 empirical input manifest contract (metadata only, no synthetic promotion)."""
REQUIRED_INPUTS = {
    "renewable_availability": ("source", "time_coverage", "technology", "timezone", "provenance"),
    "thermal_costs": ("source", "fuel_price_basis", "heat_rate_basis", "technology", "provenance"),
    "storage_parameters": ("source", "energy_capacity_mwh", "power_capacity_mw",
                           "roundtrip_efficiency", "initial_soc_policy", "provenance"),
    "interchange_boundaries": ("source", "time_coverage", "sign_convention",
                               "boundary_definition", "provenance"),
}


def audit_input_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a mapping")
    checks = {}
    for group, fields in REQUIRED_INPUTS.items():
        entry = manifest.get(group)
        missing = list(fields) if not isinstance(entry, dict) else [
            field for field in fields if entry.get(field) in (None, "", [])
        ]
        checks[group] = {
            "metadata_complete": not missing,
            "missing_fields": missing,
            "empirically_verified": bool(
                isinstance(entry, dict) and entry.get("empirically_verified") is True
                and not missing
            ),
        }
    return {
        "checks": checks,
        "all_metadata_complete": all(c["metadata_complete"] for c in checks.values()),
        "all_empirically_verified": all(c["empirically_verified"] for c in checks.values()),
        "dispatch_approved": False,  # requires load gate and numerical validation separately
    }
