"""Evidence-first generation fleet validation; no inferred fleet records."""
import csv
import math
from datetime import date, timedelta
from pathlib import Path

REQUIRED = (
    "plant_id", "generator_id", "technology", "capacity_mw",
    "balancing_authority", "online_date", "retirement_date",
    "source_name", "source_url", "source_as_of",
)


def validate_generation_fleet(csv_path, *, year, balancing_authority="CISO"):
    """Validate explicit fleet records; never impute missing dates or capacities.

    Returns a July 1 reference snapshot plus annual commissioning/retirement flags.\n    A reference snapshot is not a full-year dispatch availability profile.
    Rows outside the requested balancing authority are rejected rather than
    silently mapped from statewide generation.
    """
    if not isinstance(year, int) or isinstance(year, bool) or year < 1900 or year > 2100:
        raise ValueError("invalid model year")
    with Path(csv_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or set(reader.fieldnames) != set(REQUIRED):
            raise ValueError("generation fleet schema mismatch")
        rows = list(reader)
    if not rows:
        raise ValueError("empty generation fleet")
    seen = set()
    total = 0.0
    active = 0
    changes_during_year = 0
    reference = date(year, 7, 1)
    for index, row in enumerate(rows, 2):
        if any(row[k] is None or not str(row[k]).strip() for k in REQUIRED if k != "retirement_date"):
            raise ValueError(f"missing required generation evidence at row {index}")
        if row["balancing_authority"] != balancing_authority:
            raise ValueError(f"non-{balancing_authority} generator at row {index}")
        key = (row["plant_id"], row["generator_id"])
        if key in seen:
            raise ValueError(f"duplicate plant/generator at row {index}")
        seen.add(key)
        try:
            capacity = float(row["capacity_mw"])
            online = date.fromisoformat(row["online_date"])
            retirement = date.fromisoformat(row["retirement_date"]) if row["retirement_date"] else None
            date.fromisoformat(row["source_as_of"])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid capacity or date at row {index}") from exc
        if not math.isfinite(capacity) or capacity <= 0:
            raise ValueError(f"invalid positive capacity at row {index}")
        if retirement is not None and retirement < online:
            raise ValueError(f"retirement precedes online date at row {index}")
        if not row["source_url"].startswith(("https://", "http://")):
            raise ValueError(f"missing verifiable source URL at row {index}")
        year_start, year_end = date(year, 1, 1), date(year + 1, 1, 1)\n        if year_start <= online < year_end or (retirement is not None and year_start <= retirement < year_end):\n            changes_during_year += 1\n        if online <= reference and (retirement is None or retirement > reference):
            total += capacity
            active += 1
    return {
        "model_year": year, "balancing_authority": balancing_authority,
        "reference_date": reference.isoformat(), "fleet_rows": len(rows),
        "active_generators": active, "active_nameplate_capacity_mw": total,
        "units_with_in_year_status_changes": changes_during_year,\n        "reference_snapshot_not_annual_availability": True,\n        "hourly_availability_verified": False,
        "imports_exports_modeled": False, "dispatch_model_approved": False,
    }
