# Experiment register (planned; no empirical runs yet)

| ID | Data | Model | Calibration | Hold-out | Status |
| --- | --- | --- | --- | --- | --- |
| R00 | Synthetic UTC hourly test fixtures | Data-contract validation only | None | None | CI test fixture |
| R01 | EIA-930 BA demand (pending provenance/licensing audit) | Load audit | None | Year(s) TBD | Not started |
| R02 | R01 + independently sourced generation/capacity | PyPSA dispatch | Year(s) TBD | Year(s) TBD | Not started |
| R03 | R02 + weather covariates | Sensitivity analysis | Predeclared | Predeclared | Not started |

## Research guardrails

Do not claim model skill or reliability results before observed data, solver checks and independent hold-out validation. Record SHA256 input manifests, software versions, solver configuration, and figure-to-run traceability for each executed experiment.
