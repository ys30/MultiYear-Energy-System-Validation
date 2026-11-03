"""Stage EIA-860 battery ratings without inventing efficiencies or SOC."""
import csv
import json
import math
from pathlib import Path


def stage_verified_battery_ratings(network_nc, battery_csv, output_nc):
    import pypsa
    net = pypsa.Network(network_nc)
    if len(net.storage_units) or len(net.stores):
        raise ValueError("network already has storage")
    if not (net.generators.p_max_pu == 0).all():
        raise ValueError("unverified generation is enabled")
    with open(battery_csv, newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))
    if not records:
        raise ValueError("empty battery inventory")
    seen = set()
    energy_total = 0.0
    for r in records:
        key = (r["plant_id"], r["generator_id"])
        if key in seen:
            raise ValueError("duplicate battery ID")
        seen.add(key)
        if not all(r[k].strip().lower() == "true" for k in
                   ("energy_verified", "charge_verified", "discharge_verified")):
            raise ValueError("battery ratings not fully verified")
        values = [float(r[k]) for k in ("nameplate_power_mw", "nameplate_energy_mwh",
                                       "max_charge_mw", "max_discharge_mw")]
        if not all(math.isfinite(x) and x > 0 for x in values):
            raise ValueError("invalid battery rating")
        power, energy, charge, discharge = values
        energy_total += energy
        # Separate charge/discharge links and a Store would require an assumed
        # efficiency and initial SOC. Keep ratings in audit only, not a runnable
        # storage unit with implicit PyPSA defaults.
    output = Path(output_nc)
    output.parent.mkdir(parents=True, exist_ok=True)
    net.meta = dict(net.meta or {})
    net.meta.update({"battery_rating_inventory": "verified externally in CSV",
                     "battery_dispatch": "disabled; efficiency and SOC unknown",
                     "empirical_dispatch_ready": "false"})
    net.export_to_netcdf(output)
    restored = pypsa.Network(output)
    if len(restored.storage_units) or len(restored.stores):
        raise AssertionError("unvalidated storage became dispatchable")
    result = {"battery_count": len(records), "verified_energy_mwh": energy_total,
              "storage_dispatch_enabled": False, "efficiency_verified": False,
              "initial_soc_verified": False}
    output.with_suffix(".json").write_text(json.dumps(result, indent=2))
    print("PYPSA_BATTERY_RATINGS=" + json.dumps(result, sort_keys=True))
    return result
