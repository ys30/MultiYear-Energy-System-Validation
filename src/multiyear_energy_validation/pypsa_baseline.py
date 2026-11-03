"""Construct a transparent load-only PyPSA network, without claiming a solve."""
import csv
from pathlib import Path


def build_load_only_network(profile_csv, output_nc, *, bus="CISO", load="CISO_load"):
    """Create a network with observed load but no invented generation capacity.

    Requires optional PyPSA dependency. No optimization is performed.
    """
    try:
        import pandas as pd
        import pypsa
    except ImportError as exc:
        raise RuntimeError("Install optional dependencies: pip install pypsa pandas") from exc
    with Path(profile_csv).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["snapshot_utc", "CISO_load_mw"]:
            raise ValueError("unexpected load-profile schema")
        records = list(reader)
    if not records:
        raise ValueError("empty load profile")
    stamps = pd.to_datetime([r["snapshot_utc"] for r in records], utc=True, errors="raise")
    if stamps.has_duplicates or not stamps.is_monotonic_increasing:
        raise ValueError("snapshots must be strictly increasing and unique")
    if not ((stamps[1:] - stamps[:-1]) == pd.Timedelta(hours=1)).all():
        raise ValueError("snapshots must be contiguous hourly intervals")
    demand = pd.to_numeric([r["CISO_load_mw"] for r in records], errors="raise")
    if not pd.Series(demand).map(lambda x: pd.notna(x) and x >= 0).all():
        raise ValueError("invalid demand")
    # PyPSA/xarray NetCDF serialization works reliably with timezone-naive UTC
    # snapshots; the output metadata explicitly states the UTC convention.
    network = pypsa.Network()
    network.set_snapshots(stamps.tz_localize(None))
    network.add("Bus", bus)
    network.add("Load", load, bus=bus, p_set=demand)
    network.meta = {"source": "EIA-930 CISO observed hourly demand",
                    "snapshot_timezone": "UTC (stored naive)",
                    "interval": "hour-start",
                    "network_scope": "load-only; no generation or transmission",
                    "optimization_performed": "false"}
    output = Path(output_nc)
    output.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(output)
    return {"snapshots": len(records), "bus": bus, "load": load,
            "generation_assets": 0, "optimized": False,
            "annual_observed_mwh": float(sum(demand))}
