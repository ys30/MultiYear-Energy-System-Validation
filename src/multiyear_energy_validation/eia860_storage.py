"""Audit official EIA-860 storage power and energy, without dispatch assumptions."""
import csv
import json
import math
import zipfile
from pathlib import Path

from .eia860_fleet import _id, _records


def _positive(value):
    try:
        result = float(value)
    except (ValueError, TypeError):
        return None
    return result if math.isfinite(result) and result > 0 else None


def audit_ciso_storage(zip_path, year, battery_candidates_csv, output_dir):
    if year not in (2024, 2025):
        raise ValueError("unsupported year")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with open(battery_candidates_csv, newline="", encoding="utf-8") as stream:
        candidates = list(csv.DictReader(stream))
    ids = set()
    for item in candidates:
        if item["status_raw"] != "OP" or item["technology"] != "Batteries" or item["balancing_authority"] != "CISO":
            raise ValueError("unexpected battery candidate")
        key = (item["plant_id"], item["generator_id"])
        if key in ids:
            raise ValueError("duplicate candidate")
        ids.add(key)
    matched = {}
    with zipfile.ZipFile(zip_path) as archive:
        for row in _records(archive, f"3_4_Energy_Storage_Y{year}.xlsx", "Operable"):
            key = (_id(row.get("Plant Code")), str(row.get("Generator ID") or "").strip())
            if key not in ids:
                continue
            if key in matched:
                raise ValueError("duplicate storage workbook key")
            matched[key] = row
    fields = ["plant_id", "generator_id", "nameplate_power_mw",
              "nameplate_energy_mwh", "max_charge_mw", "max_discharge_mw",
              "duration_hours", "energy_verified", "charge_verified",
              "discharge_verified"]
    rows = []
    for item in candidates:
        key = (item["plant_id"], item["generator_id"])
        raw = matched.get(key, {})
        energy = _positive(raw.get("Nameplate Energy Capacity (MWh)"))
        charge = _positive(raw.get("Maximum Charge Rate (MW)"))
        discharge = _positive(raw.get("Maximum Discharge Rate (MW)"))
        power = _positive(item["nameplate_capacity_mw"])
        if power is None:
            raise ValueError("invalid candidate nameplate power")
        rows.append({
            "plant_id": key[0], "generator_id": key[1],
            "nameplate_power_mw": power, "nameplate_energy_mwh": energy or "",
            "max_charge_mw": charge or "", "max_discharge_mw": discharge or "",
            "duration_hours": energy / power if energy else "",
            "energy_verified": energy is not None,
            "charge_verified": charge is not None,
            "discharge_verified": discharge is not None,
        })
    with (output / "ciso_battery_storage_parameters.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "year": year, "battery_candidates": len(ids),
        "matched_storage_rows": len(matched),
        "missing_storage_rows": len(ids) - len(matched),
        "valid_energy_mwh_count": sum(r["energy_verified"] for r in rows),
        "valid_charge_mw_count": sum(r["charge_verified"] for r in rows),
        "valid_discharge_mw_count": sum(r["discharge_verified"] for r in rows),
        "nameplate_energy_mwh_verified_sum": sum(float(r["nameplate_energy_mwh"]) for r in rows if r["energy_verified"]),
        "efficiency_verified": False, "dispatch_ready": False,
    }
    (output / "ciso_storage_audit.json").write_text(json.dumps(result, indent=2))
    print("EIA860_STORAGE_AUDIT=" + json.dumps(result, sort_keys=True))
    return result
