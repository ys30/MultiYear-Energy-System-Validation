# Multi-Year Energy System Validation with PyPSA

**Private research repository — observed-load and generator-inventory staging validated; empirical dispatch not yet approved.**

This project develops reproducible multi-year CISO electricity-data harmonization and PyPSA validation. It is distinct from the [public engineering v1.0 demonstration](https://github.com/ys30/lut-to-pypsa), whose five-continent LUT demand and illustrative dispatch must not be presented as observed Western-US electricity-system results.

## Verified workflow status (2026-11-03; updated with cross-year audit)

- **2024 and 2025 CISO EIA-930 demand:** normalized hourly load inputs have 8,784 and 8,760 snapshots, respectively. The recorded annual totals are 224,030,258 MWh (2024) and 224,023,764 MWh (2025). See [load-only baseline evidence](docs/PYPSA_LOAD_ONLY_BASELINE.md).
- **Solver interface smoke test:** a 24-hour test for each year reached HiGHS optimal status using an **explicitly synthetic generator**. This validates the software path, not real generation, reliability or calibration.
- **EIA-860 annual generator fleet:** the [source intake workflow](.github/workflows/eia860-source-intake.yml) passed for both years in [run 41743257455](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41743257455). It audits CISO plant-BA assignments, operable generator nameplate capacity, and battery ratings, then stages assets with observed load in PyPSA **without empirical dispatch optimization**. Source archives and derived inventories are private CI artifacts, not evidence of hourly availability.
- **Cross-year fleet reconciliation:** [passing run 41772668659](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41772668659) matched 2,645 (2024) versus 2,786 (2025) CISO operable generator records. OP nameplate increased from **85,634.2 MW** to **92,530.0 MW** (+6,895.8 MW), with batteries **+3,862.2 MW** and solar PV **+1,849.4 MW**. Of 157 new-to-inventory records, 129 report operating year 2025 (6,201.2 MW OP) and 28 report an earlier year (138.1 MW OP). This is **inventory accounting, not independently verified commissioning**. See [technology decomposition](docs/EIA860_CISO_TECHNOLOGY_DECOMPOSITION_2024_2025.md), [operating-year cohorts](docs/EIA860_CISO_OPERATING_YEAR_COHORTS_2024_2025.md), and [status transitions](docs/EIA860_CISO_STATUS_TRANSITIONS_2024_2025.md). Three pumped-storage units changed OA→OP (+1,053 MW), not proof of new construction.
- **Research contracts:** [run 41743257483](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41743257483) passed.
- **Empirical dispatch readiness:** explicitly **false** until independently validated availability, imports/interchange, operating dates, network boundary and calibration are documented. Nameplate MW must not be treated as firm capacity or observed hourly supply.

## Next research gates

1. Preserve the verified cross-year inventory audit, source checksums and source URLs; investigate plant BA reassignment and anomalous historical-year entrants.
2. Reconcile plant-BA assignments with the CISO operating boundary and audit commissioning/retirement date precision. Keep battery power, energy and assumed efficiencies distinct.
3. Independently establish renewable and thermal hourly availability, storage constraints, and imports/exports; record uncertainty and missingness before allowing optimization.
4. Define a transparent dispatch baseline, then calibrate on 2024 and evaluate independently on 2025 with balance checks, solver diagnostics, and sensitivity analysis.
5. Produce research figures only from verified runs; keep manuscript drafts local/private.

## Scientific boundary

**No validated multi-year empirical dispatch, adequacy, transmission, emissions, cost, or reliability result is claimed.** A successful ingestion workflow or synthetic solver smoke test does not remove this boundary.

## Reproducibility and governance

Install with `pip install -e ".[test]"` and run `python -m pytest -q`. See [data validation plan](docs/DATA_VALIDATION_PLAN.md), [EIA-860 ingestion plan](docs/EIA860_INGESTION_PLAN.md), and [experiment register](docs/EXPERIMENT_REGISTER.md).

Do not commit unlicensed third-party workbooks, personal data, confidential inputs, or manuscript drafts. The research repository remains private; the public portfolio should only summarize verified, appropriately qualified engineering results.
