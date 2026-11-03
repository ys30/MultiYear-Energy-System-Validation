"""Fail-closed readiness gate for empirical hourly PyPSA dispatch inputs.

A validated annual nameplate fleet alone is insufficient for dispatch.
"""
import json
from pathlib import Path

REQUIRED_EVIDENCE = (
    "hourly_load_profile",
    "hourly_renewable_availability",
    "thermal_marginal_costs",
    "thermal_availability",
    "storage_power_and_energy_capacity",
    "storage_efficiency_and_initial_state",
    "imports_exports_boundary",
)


def assess_dispatch_readiness(fleet_audit_path, evidence, output_path=None):
    audit = json.loads(Path(fleet_audit_path).read_text())
    if not audit.get("capacity_reconciliation_passed"):
        raise ValueError("fleet capacity reconciliation must pass")
    if audit.get("dispatch_model_approved"):
        raise ValueError("annual fleet audit must not claim dispatch approval")
    if not isinstance(evidence, dict):
        raise TypeError("evidence must be a mapping")
    missing = [name for name in REQUIRED_EVIDENCE if evidence.get(name) is not True]
    result = {
        "year": audit["year"],
        "source_fleet_scope": audit["scope"],
        "empirical_dispatch_ready": not missing,
        "missing_evidence": missing,
        "evidence": {name: evidence.get(name) is True for name in REQUIRED_EVIDENCE},
        "annual_nameplate_is_not_hourly_availability": True,
    }
    if output_path is not None:
        Path(output_path).write_text(json.dumps(result, indent=2))
    return result


def require_empirical_dispatch_ready(fleet_audit_path, evidence):
    result = assess_dispatch_readiness(fleet_audit_path, evidence)
    if not result["empirical_dispatch_ready"]:
        raise RuntimeError("empirical dispatch blocked: " + ", ".join(result["missing_evidence"]))
    return result
