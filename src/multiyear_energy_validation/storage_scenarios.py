"""Explicit, non-empirical storage sensitivity scenarios.

These scenarios are *assumptions*, not EIA-observed efficiency or SOC.
No dispatch is executed by this module.
"""
import csv
import json
import math
from pathlib import Path


def build_storage_scenario(battery_csv, output_dir, *, charge_efficiency,
                           discharge_efficiency, initial_soc_fraction,
                           scenario_name):
    for name, value in (
        ("charge_efficiency", charge_efficiency),
        ("discharge_efficiency", discharge_efficiency),
        ("initial_soc_fraction", initial_soc_fraction),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be finite numeric")
    if not 0 < charge_efficiency <= 1 or not 0 < discharge_efficiency <= 1:
        raise ValueError("efficiencies must be in (0, 1]")
    if not 0 <= initial_soc_fraction <= 1:
        raise ValueError("initial SOC fraction must be in [0, 1]")
    if not scenario_name or not scenario_name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("scenario_name must be alphanumeric with _ or -")
    with open(battery_csv, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("empty battery dataset")
    seen = set()
    staged = []
    for r in rows:
        key = (r["plant_id"], r["generator_id"])
        if key in seen:
            raise ValueError("duplicate battery ID")
        seen.add(key)
        if not all(r[k].strip().lower() == "true" for k in
                   ("energy_verified", "charge_verified", "discharge_verified")):
            raise ValueError("unverified storage rating")
        vals = [float(r[k]) for k in ("nameplate_energy_mwh", "max_charge_mw", "max_discharge_mw")]
        if not all(math.isfinite(v) and v > 0 for v in vals):
            raise ValueError("invalid storage rating")
        energy, charge, discharge = vals
        staged.append({
            "plant_id": key[0], "generator_id": key[1],
            "energy_capacity_mwh_observed": energy,
            "max_charge_mw_observed": charge,
            "max_discharge_mw_observed": discharge,
            "charge_efficiency_assumed": charge_efficiency,
            "discharge_efficiency_assumed": discharge_efficiency,
            "initial_soc_fraction_assumed": initial_soc_fraction,
            "initial_soc_mwh_assumed": energy * initial_soc_fraction,
        })
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    columns = list(staged[0])
    with (out / f"storage_scenario_{scenario_name}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(staged)
    result = {
        "scenario_name": scenario_name, "battery_count": len(staged),
        "total_energy_mwh_observed": sum(x["energy_capacity_mwh_observed"] for x in staged),
        "initial_soc_mwh_assumed": sum(x["initial_soc_mwh_assumed"] for x in staged),
        "charge_efficiency_assumed": charge_efficiency,
        "discharge_efficiency_assumed": discharge_efficiency,
        "round_trip_efficiency_assumed": charge_efficiency * discharge_efficiency,
        "initial_soc_fraction_assumed": initial_soc_fraction,
        "scenario_only": True, "empirical_dispatch_ready": False,
        "optimization_performed": False,
    }
    (out / f"storage_scenario_{scenario_name}.json").write_text(json.dumps(result, indent=2))
    print("STORAGE_SCENARIO=" + json.dumps(result, sort_keys=True))
    return result
