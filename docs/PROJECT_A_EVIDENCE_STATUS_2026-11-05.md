# Project A — evidence and milestone status (2026-11-05)

This is a public-safe engineering status note, **not** the private manuscript.

| Stage | Evidence | Status |
| --- | --- | --- |
| R00 | Synthetic PyPSA/HiGHS smoke | Passed |
| R01 | CISO EIA-860 2024–2025 capacity comparison | Verified |
| R02a | EIA-930 demand/fuel observations, audit, normalized annual artifacts | Export successful; known quality exceptions |
| R02 | Empirical PyPSA dispatch | Blocked: renewable availability, thermal cost, storage and boundary inputs not independently verified |
| R03 | Weather sensitivity / multiyear out-of-sample validation | Not run |

Observed CISO EIA-930 demand totals: 2024 = 224,030,258 MWh, 2025 = 224,023,764 MWh. EIA-860 capacity comparisons: 2024 = 85,634.2 MW, 2025 = 92,530 MW; differences must not automatically be described as new builds.

Critical audit exceptions: 2024-11-02T08 to 2024-11-03T07 UTC has D observations but no NG/TI/fuel observations; 2025-07-31T21 demand outlier and fuel/region mismatch; GEO first separately reported at 2025-12-16T09. No missing value was silently imputed. Annual normalized CSV artifacts and checksums are documented in `R02_NORMALIZED_FUEL_DATA_CONTRACT.md`.

Next evidence milestone: obtain and validate a bounded 2024/2025 ERA5 sample, confirm SSRD hourly accumulation and time alignment, then build independently calibrated solar/wind potential. `era5_units.py` enforces explicit one-hour SSRD conversion; it does not establish that a downloaded ERA5 value has the required interval semantics.

**Manuscript readiness:** Methods for source audit and data provenance are documentable; empirical optimization results, sensitivity, model validation and final conclusions are not yet supportable. The manuscript stays private and is not included in this repository.
