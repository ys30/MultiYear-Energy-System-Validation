"""Construct a transparent load-only PyPSA network, without claiming a solve."""
import csv
import math
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
    if not pd.Series(demand).map(lambda x: pd.notna(x) and math.isfinite(x) and x >= 0).all():
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
    restored = pypsa.Network(output)
    if len(restored.snapshots) != len(records) or len(restored.loads) != 1:
        raise ValueError("PyPSA NetCDF round-trip changed snapshot or load count")
    actual = restored.loads_t.p_set[load].to_numpy()
    if len(actual) != len(demand) or not all(
        math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-6)
        for a, b in zip(actual, demand)
    ):
        raise ValueError("PyPSA NetCDF round-trip changed observed load values")
    return {"snapshots": len(records), "bus": bus, "load": load,
            "generation_assets": 0, "optimized": False,
            "annual_observed_mwh": float(sum(demand))}


def solve_synthetic_balance_smoke_test(profile_csv, *, snapshots=24):
    """Synthetic feasibility test only: NOT an empirical generation model.

    Use the first N observed load hours, one unlimited-costed synthetic
    generator and one bus. Check that optimization exactly meets demand.
    """
    if not isinstance(snapshots, int) or isinstance(snapshots, bool) or not 1 <= snapshots <= 168:
        raise ValueError("snapshots must be between 1 and 168")
    try:
        import pandas as pd
        import pypsa
    except ImportError as exc:
        raise RuntimeError("Install pypsa and pandas") from exc
    frame = pd.read_csv(profile_csv, nrows=snapshots)
    if len(frame) != snapshots or list(frame.columns) != ["snapshot_utc", "CISO_load_mw"]:
        raise ValueError("unexpected or incomplete input profile")
    stamps = pd.to_datetime(frame["snapshot_utc"], utc=True, errors="raise")
    if stamps.has_duplicates or not stamps.is_monotonic_increasing:
        raise ValueError("invalid snapshot ordering")
    if snapshots > 1 and not ((stamps.iloc[1:].reset_index(drop=True)
                                - stamps.iloc[:-1].reset_index(drop=True))
                               == pd.Timedelta(hours=1)).all():
        raise ValueError("noncontiguous timestamps")
    demand = pd.to_numeric(frame["CISO_load_mw"], errors="raise")
    if not demand.map(lambda x: math.isfinite(x) and x >= 0).all():
        raise ValueError("invalid load")
    network = pypsa.Network()
    network.set_snapshots(stamps.dt.tz_localize(None))
    network.add("Bus", "CISO")
    network.add("Load", "observed_CISO_demand", bus="CISO", p_set=demand.to_numpy())
    # Deliberately fictitious dispatchable capacity: feasibility test only.
    network.add("Generator", "synthetic_unlimited_supply", bus="CISO",
                p_nom=max(float(demand.max()), 1.0) * 1.01,
                marginal_cost=1.0)
    status, condition = network.optimize(solver_name="highs")
    if status != "ok" or condition != "optimal":
        raise ValueError(f"synthetic smoke optimization failed: {status}/{condition}")
    generation = network.generators_t.p["synthetic_unlimited_supply"].to_numpy()
    max_error = max(abs(float(a) - float(b)) for a, b in zip(generation, demand))
    if max_error > 1e-5:
        raise ValueError("synthetic generator does not balance observed load")
    return {"snapshots": snapshots, "solver_status": status,
            "solver_condition": condition, "max_balance_error_mw": max_error,
            "synthetic_generator": True, "empirical_generation_validated": False,
            "research_result": False}
