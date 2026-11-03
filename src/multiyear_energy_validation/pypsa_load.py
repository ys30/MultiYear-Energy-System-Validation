"""Strict, reproducible PyPSA load input preparation; no model calibration claims."""
import calendar
import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def build_pypsa_load_profile(source_csv, output_csv, *, year, region="CISO"):
    """Produce a one-column MW load profile indexed by UTC interval start.

    Fail closed on missing, duplicate, out-of-year or invalid observations.
    This output can be assigned to network.loads_t.p_set; it does not
    construct a generation fleet or claim simulated power-system results.
    """
    if not isinstance(year, int) or isinstance(year, bool) or not 1900 <= year <= 9998:
        raise ValueError("invalid model year")
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    n = (366 if calendar.isleap(year) else 365) * 24
    expected = [start + timedelta(hours=i) for i in range(n)]
    observed = {}
    with Path(source_csv).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"time_utc", "balancing_authority", "demand_mw"}.issubset(reader.fieldnames or []):
            raise ValueError("missing normalized load columns")
        for row in reader:
            if row["balancing_authority"] != region:
                raise ValueError("unexpected balancing authority")
            try:
                stamp = datetime.fromisoformat(row["time_utc"].replace("Z", "+00:00"))
                mw = float(row["demand_mw"])
            except (ValueError, TypeError, AttributeError) as exc:
                raise ValueError("invalid timestamp or demand") from exc
            if (stamp.tzinfo is None or stamp.utcoffset() != timedelta(0)
                    or stamp.minute or stamp.second or stamp.microsecond):
                raise ValueError("timestamp must be UTC hour start")
            if not start <= stamp < start + timedelta(hours=n):
                raise ValueError("timestamp outside model year")
            if stamp in observed:
                raise ValueError("duplicate UTC timestamp")
            if not math.isfinite(mw) or mw < 0:
                raise ValueError("invalid MW")
            observed[stamp] = mw
    if len(observed) != n or any(stamp not in observed for stamp in expected):
        raise ValueError(f"incomplete model-year load: {len(observed)}/{n} UTC hours")
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["snapshot_utc", "CISO_load_mw"])
        writer.writerows((stamp.isoformat(), observed[stamp]) for stamp in expected)
    return {"year": year, "region": region, "snapshots": n,
            "annual_observed_mwh": sum(observed.values()),
            "min_load_mw": min(observed.values()),
            "max_load_mw": max(observed.values()),
            "model_simulated": False}
