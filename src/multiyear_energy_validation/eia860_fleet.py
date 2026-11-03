"""Audit CAISO EIA-860 operable nameplate capacity without dispatch claims."""
import csv
import io
import json
import math
import zipfile
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook


def _records(archive, filename, sheet):
    with archive.open(filename) as stream:
        book = load_workbook(io.BytesIO(stream.read()), read_only=True, data_only=True)
        try:
            ws = book[sheet]
            rows = ws.iter_rows(values_only=True)
            next(rows)  # EIA title row
            headers = [str(v).strip() if v is not None else "" for v in next(rows)]
            for row in rows:
                if not any(v is not None for v in row):
                    continue
                yield dict(zip(headers, row))
        finally:
            book.close()


def _id(value):
    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, (float, int)):
        if not math.isfinite(float(value)) or int(value) != value:
            return ""
        return str(int(value))
    return str(value).strip()


def audit_ciso_operable(zip_path, year, output_dir):
    """Use plant BA code and generator Operable sheet; flag ambiguous records."""
    if year not in (2024, 2025):
        raise ValueError("unsupported year")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        plants = {}
        for row in _records(archive, f"2___Plant_Y{year}.xlsx", "Plant"):
            plant = _id(row.get("Plant Code"))
            if plant in plants:
                raise ValueError(f"duplicate plant code: {plant}")
            plants[plant] = str(row.get("Balancing Authority Code") or "").strip()
        counts = Counter()
        tech_mw = Counter()
        status_counts = Counter()
        status_mw = Counter()
        status_technology_mw = Counter()
        rejected_examples = []
        accepted = []
        seen = set()
        for row in _records(archive, f"3_1_Generator_Y{year}.xlsx", "Operable"):
            plant = _id(row.get("Plant Code"))
            if plant not in plants:
                counts["unmatched_plant"] += 1
                if len(rejected_examples) < 20:
                    rejected_examples.append({"reason": "unmatched_plant", "plant_id": plant, "generator_id": str(row.get("Generator ID") or "")})
                continue
            if plants[plant] != "CISO":
                continue
            counts["ciso_operable_rows"] += 1
            gen = str(row.get("Generator ID") or "").strip()
            key = (plant, gen)
            if not gen or key in seen:
                counts["invalid_or_duplicate_id"] += 1
                continue
            seen.add(key)
            try:
                mw = float(row["Nameplate Capacity (MW)"])
            except (TypeError, ValueError):
                counts["invalid_capacity"] += 1
                continue
            if not math.isfinite(mw) or mw <= 0:
                counts["invalid_capacity"] += 1
                continue
            tech = str(row.get("Technology") or "").strip()
            status = str(row.get("Status") or "").strip()
            if not tech or not status:
                counts["missing_technology_or_status"] += 1
                continue
            status_counts[status] += 1
            status_mw[status] += mw
            status_technology_mw[(status, tech)] += mw
            accepted.append({
                "plant_id": plant, "generator_id": gen, "technology": tech,
                "status_raw": status, "nameplate_capacity_mw": mw,
                "operating_month_raw": row.get("Operating Month"),
                "operating_year_raw": row.get("Operating Year"),
                "planned_retirement_month_raw": row.get("Planned Retirement Month"),
                "planned_retirement_year_raw": row.get("Planned Retirement Year"),
                "balancing_authority": "CISO",
            })
            tech_mw[tech] += mw
            counts["accepted_rows"] += 1
    with (output / "ciso_operable_generators.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["plant_id", "generator_id", "technology", "status_raw",
                  "nameplate_capacity_mw", "operating_month_raw", "operating_year_raw",
                  "planned_retirement_month_raw", "planned_retirement_year_raw",
                  "balancing_authority"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(accepted)
    result = {
        "year": year, "scope": "EIA-860 plant BA code CISO; Operable sheet",
        "counts": dict(counts), "status_counts": dict(sorted(status_counts.items())),
        "rejected_examples": rejected_examples,
        "nameplate_mw_by_status": dict(sorted(status_mw.items())),
        "nameplate_mw_by_status_and_technology": [
            {"status": status, "technology": technology, "nameplate_mw": capacity}
            for (status, technology), capacity in sorted(status_technology_mw.items())
        ],
        "nameplate_mw_by_technology": dict(sorted(tech_mw.items())),
        "total_nameplate_mw": sum(tech_mw.values()),
        "hourly_availability_verified": False, "dispatch_model_approved": False,
        "retirement_dates_are_planned_not_actual": True,
    }
    (output / "ciso_fleet_audit.json").write_text(json.dumps(result, indent=2))
    print("EIA860_CISO_FLEET_AUDIT=" + json.dumps(result, sort_keys=True))
    return result
