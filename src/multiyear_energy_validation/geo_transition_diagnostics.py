"""Assess observed GEO/OTH transition without assuming causal reclassification."""


def adjacent_transition(before, after):
    if before["geo_reported"] or not after["geo_reported"]:
        raise ValueError("requires adjacent GEO absent-to-present observations")
    if before["geo_mwh"] is not None or after["geo_mwh"] is None:
        raise ValueError("invalid GEO reporting state")
    delta_other = after["other_mwh"] - before["other_mwh"]
    delta_total = after["fuel_sum_mwh"] - before["fuel_sum_mwh"]
    return {
        "before_period": before["period"],
        "after_period": after["period"],
        "newly_reported_geo_mwh": after["geo_mwh"],
        "other_change_mwh": delta_other,
        "geo_plus_other_change_mwh": after["geo_mwh"] + delta_other,
        "total_generation_change_mwh": delta_total,
        "reclassification_proven": False,
        "requires_provider_definition": True,
    }
