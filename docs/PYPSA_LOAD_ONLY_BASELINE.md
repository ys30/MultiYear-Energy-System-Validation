# Load-only PyPSA baseline: no optimization claims

Verified EIA-930 CISO model-year input manifests from GitHub Actions run
https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41679645696 :

| Model year | UTC hourly snapshots | Observed demand energy (MWh) | Min MW | Max MW |
| --- | ---: | ---: | ---: | ---: |
| 2024 | 8784 | 224030258 | 14794 | 47571 |
| 2025 | 8760 | 224023764 | 11819 | 43860 |

The artifact `pypsa_load_profile.csv` is produced only for complete normalized years.
A new optional builder `multiyear_energy_validation.pypsa_baseline.build_load_only_network`
can create a single-bus, single-load PyPSA NetCDF file using that profile.

**This is an input/network serialization smoke test, not a solvable
electricity-system model.** No generators, storage, links, lines, costs,
renewable profiles, imports, or dispatch decisions are fabricated. No
optimization, reliability, emissions, or calibration results may be inferred.

To execute locally, first download the private GitHub Actions artifact for
2024 or 2025, then install PyPSA separately and call:

```python
from multiyear_energy_validation.pypsa_baseline import build_load_only_network
print(build_load_only_network(
    "pypsa_load_profile.csv", "load_only_network.nc"))
```

Future work: validate the NetCDF round trip in CI, independently source
generation capacities and availability, define network boundaries, and only
then formulate a solvable baseline with explicitly documented assumptions.

## Verified PyPSA solver smoke test (2026-11-03)

GitHub Actions run https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41687067870 succeeded for all five intake jobs. For **2024 and 2025 only**, the optional PyPSA smoke step used 24 observed CISO hourly loads with one deliberately synthetic dispatchable generator. Both HiGHS optimizations returned `status=ok`, `condition=optimal`, and `max_balance_error_mw=0.0`. Each smoke manifest explicitly records `synthetic_generator=true`, `empirical_generation_validated=false`, `research_result=false`.

This demonstrates numerical feasibility of the data-to-solver path, **not** real-world supply adequacy, cost, capacity, reliability, or prediction accuracy.

## Minimum evidence needed before an empirical supply model

1. **System boundary:** identify whether the study models CAISO balancing-authority demand only, California statewide generation, or a larger western interconnection. These are not interchangeable. Record imports, exports and interchange treatment.
2. **Generation fleet:** choose a reproducible source with plant/unit IDs, technology, nameplate capacity, commissioning/retirement dates and mapping to the modeled balancing authority. Audit year-specific capacity changes; do not assign statewide fleet indiscriminately to CAISO.
3. **Hourly supply availability:** verify fuel-specific hourly profiles, hydro constraints, outages and renewable capacity factors against independently sourced time series. EIA-930 aggregate generation by fuel is not automatically equivalent to installed capacity or maximum availability.
4. **Storage and trade:** document charging/discharging efficiency, state-of-charge, imports, exports, and any external supply assumptions. A closed single-bus CAISO model may otherwise invent scarcity.
5. **Optimization and validation:** specify solver, objective, dispatch constraints, baseline calibration, and out-of-sample validation. Reserve 2025 for validation when fitting any parameters on 2024.
6. **Scientific honesty:** preserve raw observed data separately, report missingness and source provenance, and never label the synthetic 24-hour smoke test as empirical simulation.
