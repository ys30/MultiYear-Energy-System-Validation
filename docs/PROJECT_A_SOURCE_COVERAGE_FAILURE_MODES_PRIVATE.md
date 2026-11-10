# Project A — verified source coverage and failure-mode inventory (private)

**Verification:** CI run [42879024191](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42879024191), commit `40db359d`, successful; research contracts [42879024249](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42879024249): 176 passed, 1 skipped.

## Table R02-D1 — source granularity and evidence boundaries

| Source | Native observable | Case-study period | Verified coverage or concrete issue | Can support | Cannot independently establish |
|---|---|---|---|---|---|
| EIA-860 | Generator inventory, nameplate, technology, operational status and commissioning vintage | 2024–2025 | CISO-associated operating nameplate: 85,634.2 MW (2024); 92,530.0 MW (2025). Annual snapshot, not uniform within-year availability | Plant inventory and capacity-vintage checks | Plant-hour production or equipment power curve |
| EIA-923 | Plant–fuel monthly net generation | 2024–2025 | Three wind sites have 12 monthly values per year for the reported resource–generation comparison | Observed monthly output and month-length-normalized daily output | Generator-level attribution in mixed plants; hourly renewable availability |
| EIA-930 | BA-level hourly demand and fuel-reported generation | 2024–2025 | 2024 demand 8,784 hours; 2025 demand 8,760 hours. 2025-07-31 21 UTC demand anomaly; 2024-11-02–03 fuel-report gap | System-level demand coverage, temporal anomaly screening | Plant-level dispatch or complete hourly fuel reporting |
| NASA POWER | Gridded hourly meteorology (including WS10M and GHI) | Pilot weather sample, 2025 July; wind monthly analysis 2024–2025 | July 2025 six-site sample: 6 × 744 = 4,464 site-hours | Meteorological context and resource proxies | Validated turbine hub-height wind or hourly power output |
| Plant engineering registry | Explicit unknown/scenario/documented engineering slots | Six pilot sites | 39 engineering parameter slots, none promoted in current baseline | Traceable parameter gap inventory | Calibrated plant physics without independent evidence |
| Dispatch readiness v2 | Scope-aware evidence decisions | Six-site baseline | 44 blocked gates; zero screen-only and zero not-applicable; dispatch not approved | Auditable decision under declared policy | Proof that all possible sources are absent or that a scenario PyPSA model is impossible |

**Denominator rules:** The EIA-930 hours refer to the stated calendar-year demand series, not the completeness of every fuel column. The 4,464 NASA POWER site-hours refer specifically to the July 2025 six-site sample, not to a two-year complete meteorological archive for all six sites. Annual EIA-860 nameplate is not a direct estimate of installed capacity at every hour of the year.

## Table R02-D2 — concrete validation failure modes

| Failure mode | Evidence in case study | Validation response | Consequence for claims |
|---|---|---|---|
| Annual capacity snapshot vs operating vintage | Wind plant 7526 includes an 85.5 MW unit commissioned May 2024 | Preserve commissioning vintage and year-specific scope | Avoid attributing all 2024 monthly output to year-end installed capacity |
| Post-period commissioning | Solar plant 64210 commissioned after July 2025 | Exclude from observed operating July pilot interpretation | Weather at a site does not imply operational generation |
| Isolated demand anomaly | CISO demand at 2025-07-31 21 UTC: 11,819 MWh vs adjacent 29,881/29,886 MWh | Flag; sensitivity only; do not silently repair as observed | Protect aggregate load statistics from unreported correction |
| Fuel-series missingness | EIA-930 fuel records missing 2024-11-02–03 | Keep missing distinct from physical zero | Avoid fictitious zero-fuel generation |
| Late reporting coverage | EIA-930 GEO first reported 2025-12-16 | Treat pre-report missingness as reporting scope, not zero | Avoid spurious technology trend |
| Plant-hour weather/output mismatch | NASA POWER WS10M vs EIA-923 monthly plant-fuel generation | Use descriptive monthly associations, LOMO and matched-month contrasts | Correlation is not calibrated plant-hour availability |
| Parameter-source mismatch | EIA-860 nameplate without turbine curve/PV equipment details | Keep 39 slots unknown and block empirical promotion | Prevent unsupported engineering assumptions |
| Missing dispatch system evidence | Five required system gates unverified | Fail closed and report JSON decisions | No empirical hourly dispatch approval |

## Results paragraph (candidate)

*The multi-source validation workflow identified several distinct classes of temporal and semantic mismatch. The EIA-930 demand series covered 8,784 and 8,760 hourly records in 2024 and 2025, respectively, while fuel-report completeness differed from demand coverage. An isolated 2025 demand anomaly and a 2024 fuel-report gap were flagged without silently converting missing or suspicious values into observations. Generator commissioning history also prevented interpreting year-end EIA-860 capacity as uniform within-year operational availability. The six-site July 2025 NASA POWER extract contained 4,464 site-hours, but these meteorological records were not treated as observed renewable production. These source-level boundaries carried through to the readiness audit, which withheld empirical hourly dispatch approval because 39 plant engineering parameter slots and five system-level requirements remained unverified.*

## Limitations of this table

This is a **verified-case-study inventory**, not a new comprehensive coverage audit. Counts above combine previously validated workflow results with the current successful CI baseline; the document does not assert that every historical number was recomputed in run 42879024191. A future reproducible coverage export should materialize all table values from one versioned machine-readable manifest and check them automatically.
