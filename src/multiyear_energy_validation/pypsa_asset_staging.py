"""Stage audited EIA-860 CISO assets in PyPSA without fictitious dispatch."""
import csv
import json
import math
from pathlib import Path


def _read(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def build_asset_staging_network(nonbattery_csv, battery_csv, output_nc):
    """Represent OP non-battery generators and battery power inventory.

    Battery units are NOT created as StorageUnit because EIA-860 nameplate
    power alone does not establish MWh, duration, efficiency or SOC.
    No optimization is performed; battery power remains in sidecar audit.
    """
    try:
        import pypsa
    except ImportError as exc:
        raise RuntimeError("Install pypsa to stage asset inventory") from exc
    generators = _read(nonbattery_csv)
    batteries = _read(battery_csv)
    network = pypsa.Network()
    network.add("Bus", "CISO")
    seen = set()
    gen_mw = 0.0
    battery_mw = 0.0
    for kind, records in (("generator", generators), ("battery", batteries)):
        for row in records:
            if row.get("balancing_authority") != "CISO" or row.get("status_raw") != "OP":
                raise ValueError("only audited CISO OP assets are permitted")
            is_battery = row.get("technology") == "Batteries"
            if is_battery != (kind == "battery"):
                raise ValueError("resource classification mismatch")
            key = (row["plant_id"], row["generator_id"])
            if not all(key) or key in seen:
                raise ValueError("empty or duplicate plant/generator identity")
            seen.add(key)
            mw = float(row["nameplate_capacity_mw"])
            if not math.isfinite(mw) or mw <= 0:
                raise ValueError("invalid nameplate capacity")
            if kind == "battery":
                battery_mw += mw
                continue
            gen_mw += mw
            network.add("Generator", f"{key[0]}::{key[1]}", bus="CISO",
                        p_nom=mw, carrier=str(row["technology"]),
                        p_max_pu=0.0)
    network.meta = {
        "scope": "EIA-860 CISO OP asset staging; not dispatch",
        "generator_p_max_pu": "0 pending hourly availability",
        "battery_handling": "excluded from network pending energy and efficiency evidence",
        "optimization_performed": "false",
    }
    output = Path(output_nc)
    output.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(output)
    restored = pypsa.Network(output)
    if len(restored.generators) != len(generators):
        raise AssertionError("NetCDF roundtrip changed generator count")
    if not math.isclose(float(restored.generators.p_nom.sum()), gen_mw, abs_tol=1e-5):
        raise AssertionError("NetCDF roundtrip changed generator nameplate MW")
    # Every generator must remain disabled until independently sourced
    # hourly availability is attached. Guard against NetCDF attribute loss.
    if not (restored.generators.p_max_pu == 0.0).all():
        raise AssertionError("NetCDF roundtrip enabled unvalidated generators")
    if len(restored.storage_units) or len(restored.stores):
        raise AssertionError("unvalidated storage was introduced")
    result = {
        "generator_count": len(generators), "generator_nameplate_mw": gen_mw,
        "battery_count_not_modeled": len(batteries),
        "battery_power_nameplate_mw_not_modeled": battery_mw,
        "optimization_performed": False, "empirical_dispatch_ready": False,
    }
    output.with_suffix(".json").write_text(json.dumps(result, indent=2))
    print("PYPSA_ASSET_STAGING=" + json.dumps(result, sort_keys=True))
    return result
