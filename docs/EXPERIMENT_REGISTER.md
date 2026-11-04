# Experiment register — verified data audits and pending dispatch

This register separates empirical **input-data audits** from model validation and dispatch. A successful CI audit does not imply a calibrated, observed-data PyPSA simulation.

| ID | Data | Workstream | Validation | Status |
| --- | --- | --- | --- | --- |
| R00 | Synthetic UTC hourly fixtures | Data contracts and solver smoke checks | CI tests; synthetic 24-hour HiGHS solve optimal with zero balance residual | **Completed: synthetic only** |
| R01 | EIA-930 CISO BA hourly demand, 2024 and 2025 | Observed demand intake and annual totals | 2024: 224,030,258 MWh / 8,784 hours; 2025: 224,023,764 MWh / 8,760 hours | **Completed: data audit only** |
| R01b | Official EIA-860 2024/2025 CISO Operable generator inventory | Plant BA and generator status/nameplate reconciliation | 2024 OP: 85,634.2 MW; 2025 OP: 92,530.0 MW; delta +6,895.8 MW | **Completed: annual inventory audit** |
| R01c | EIA-860 cross-year generator identities and operating-year fields | Technology/status transitions and reported operating-year cohorts | 157 new-to-inventory records; 129 report 2025 operating year (6,201.2 OP MW); 28 earlier years (138.1 OP MW). CI run 41772668659 | **Completed: inventory accounting, not independently verified commissioning** |
| R01d | EIA-860 matched generator status transitions, 2024–2025 | Unit-level status and operating-date audit | 42 status changes, +862.4 MW OP accounting contribution; all 42 retain identical reported operating month/year; CI 41774641358 | **Completed: verified status-accounting audit** |
| R02 | R01 + independently validated hourly generation/availability, interchange, storage parameters and costs | Observed-data PyPSA dispatch | Physical consistency, solver, independent validation | **Blocked: empirical input readiness incomplete** |
| R03 | R02 + weather covariates | Sensitivity and scenario experiments | Predeclared scenarios and holdout | **Not started; depends on R02** |

## Verified provenance and interpretation

- [EIA-860 technology decomposition](EIA860_CISO_TECHNOLOGY_DECOMPOSITION_2024_2025.md)
- [EIA-860 status transitions](EIA860_CISO_STATUS_TRANSITIONS_2024_2025.md)
- [EIA-860 operating-year cohorts](EIA860_CISO_OPERATING_YEAR_COHORTS_2024_2025.md)
- [Unit-level audit of all 42 status changes](EIA860_CISO_ALL_STATUS_CHANGE_UNIT_AUDIT_2024_2025.md)
- [Pumped-storage historical operating-date audit](EIA860_CISO_PUMPED_STORAGE_STATUS_AUDIT_2024_2025.md)
- [Passing operating-year capacity workflow](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41772668659)

**Interpretation guardrails:** A newly appearing generator identity is not proof of construction; reported operating year is not independently verified commissioning; OP nameplate MW is not hourly availability; batteries' MW alone does not specify MWh or duration. In particular, three pumped-storage units changed OA→OP (+1,053 MW); this is a status transition, not evidence of 1,053 MW of newly built pumped storage.

## R02 readiness gates

1. Independently verify hourly renewable and thermal availability and time-zone/BA consistency.
2. Validate CISO interchange and the chosen system boundary; document treatment of imports/exports.
3. Obtain storage energy capacity, duration, charge/discharge efficiencies and initial state assumptions.
4. Establish defensible operating costs, outage and curtailment assumptions.
5. Archive source checksums, input manifests, solver versions, time alignment and figure-to-run traceability.
6. Run calibration and independent holdout validation before making adequacy or model-skill claims.

**Empirical dispatch ready: false.** The research manuscript remains outside the GitHub repository.
