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
