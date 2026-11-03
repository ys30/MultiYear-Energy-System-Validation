"""Build non-solved PyPSA storage sensitivity network with explicit provenance.

Two one-way Links plus a Store preserve distinct charge/discharge ratings.
No generator availability or dispatch eligibility is inferred.
"""
import csv
import json
import math
from pathlib import Path


def build_storage_scenario_network(joint_network_nc, scenario_csv, output_nc):
    import pypsa
    network = pypsa.Network(joint_network_nc)
    if len(network.storage_units) or len(network.stores):
        raise ValueError("storage already present")
    if not (network.generators.p_max_pu == 0.0).all():
        raise ValueError("unvalidated generators are enabled")
    with open(scenario_csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("empty scenario")
    seen = set()
    energy_total = 0.0
    for row in rows:
        key = (row["plant_id"], row["generator_id"])
        if key in seen:
            raise ValueError("duplicate battery")
        seen.add(key)
        values = [float(row[k]) for k in (
            "energy_capacity_mwh_observed", "max_charge_mw_observed",
            "max_discharge_mw_observed", "charge_efficiency_assumed",
            "discharge_efficiency_assumed", "initial_soc_fraction_assumed",
            "initial_soc_mwh_assumed")]
        energy, charge, discharge, eta_c, eta_d, soc_fraction, soc = values
        if not all(math.isfinite(x) for x in values):
            raise ValueError("nonfinite scenario values")
        if not (energy > 0 and charge > 0 and discharge > 0 and
                0 < eta_c <= 1 and 0 < eta_d <= 1 and 0 <= soc_fraction <= 1 and
                math.isclose(soc, energy * soc_fraction, rel_tol=1e-9, abs_tol=1e-6)):
            raise ValueError("invalid scenario physics")
        name = "battery_" + "_".join(key)
        bus = name + "_internal"
        network.add("Bus", bus)
        network.add("Store", name, bus=bus, e_nom=energy,
                    e_initial=soc, e_cyclic=False, e_min_pu=0, e_max_pu=1)
        network.add("Link", name + "_charge", bus0="CISO", bus1=bus,
                    p_nom=charge, efficiency=eta_c, p_min_pu=0)
        network.add("Link", name + "_discharge", bus0=bus, bus1="CISO",
                    p_nom=discharge, efficiency=eta_d, p_min_pu=0)
        energy_total += energy
    output = Path(output_nc)
    output.parent.mkdir(parents=True, exist_ok=True)
    network.meta = dict(network.meta or {})
    network.meta.update({"storage_parameters": "observed ratings; assumed efficiencies and SOC",
                         "storage_scenario_only": "true",
                         "optimized": "false",
                         "empirical_dispatch_ready": "false"})
    network.export_to_netcdf(output)
    restored = pypsa.Network(output)
    if (len(restored.stores) != len(rows) or len(restored.links) != 2 * len(rows)
            or not (restored.generators.p_max_pu == 0.0).all()
            or not math.isclose(float(restored.stores.e_nom.sum()), energy_total, abs_tol=1e-5)):
        raise AssertionError("scenario NetCDF roundtrip failed")
    result = {"battery_count": len(rows), "storage_links": len(restored.links),
              "energy_capacity_mwh": energy_total, "snapshots": len(restored.snapshots),
              "scenario_only": True, "optimization_performed": False,
              "empirical_dispatch_ready": False}
    output.with_suffix(".json").write_text(json.dumps(result, indent=2))
    print("PYPSA_STORAGE_SCENARIO_NETWORK=" + json.dumps(result, sort_keys=True))
    return result
