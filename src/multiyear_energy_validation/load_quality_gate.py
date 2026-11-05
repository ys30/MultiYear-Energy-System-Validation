"""Conservative R02a load-anomaly handling policy.

Original hourly load is immutable. Scenario substitutions are never silently
promoted to empirical source corrections or dispatch-ready inputs.
"""
from dataclasses import dataclass

ANOMALY_HOUR_UTC = "2025-07-31T20:00:00+00:00"


@dataclass(frozen=True)
class LoadQualityDecision:
    hour_utc: str
    source_observation_mwh: float
    scenario_observation_mwh: float | None
    empirical_approved: bool
    classification: str


def classify_load_hour(hour_utc, observed_mwh, *, scenario_value=None):
    if observed_mwh < 0:
        raise ValueError("negative demand")
    if hour_utc != ANOMALY_HOUR_UTC:
        if scenario_value is not None:
            raise ValueError("scenario substitution only permitted for flagged hour")
        return LoadQualityDecision(hour_utc, observed_mwh, None, True, "unflagged")
    if scenario_value is not None and scenario_value < 0:
        raise ValueError("negative scenario demand")
    return LoadQualityDecision(
        hour_utc=hour_utc,
        source_observation_mwh=observed_mwh,
        scenario_observation_mwh=scenario_value,
        empirical_approved=False,
        classification="independent_source_shape_conflict_pending_provider_resolution",
    )


def decide_dispatch_gate(decisions, *, renewable_availability=False,
                         thermal_costs=False, storage_parameters=False,
                         interchange_boundaries=False):
    decisions = list(decisions)
    unresolved = [d.hour_utc for d in decisions if not d.empirical_approved]
    missing = [name for name, value in (
        ("renewable_availability", renewable_availability),
        ("thermal_costs", thermal_costs),
        ("storage_parameters", storage_parameters),
        ("interchange_boundaries", interchange_boundaries),
    ) if not value]
    return {
        "r02_empirical_dispatch_approved": not unresolved and not missing and bool(decisions),
        "unresolved_load_hours": unresolved,
        "missing_inputs": missing,
        "scenario_values_do_not_resolve_source_quality": True,
    }
