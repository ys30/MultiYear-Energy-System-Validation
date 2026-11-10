# R02 empirical dispatch readiness — verified manuscript Results (private)

**Evidence:** [R02 CI run 42854166545](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42854166545), commit `bee6dc59`, completed successfully. The report is emitted as `outputs/spatial_weather_merged_2025/empirical_dispatch_readiness.json` in the archived workflow artifact.

## Verified quantitative outcome

| Measure | Verified value | Meaning |
|---|---:|---|
| Pilot plants audited | 6 | Three solar and three wind sites in the pilot |
| Plant engineering parameter slots | 39 | 3 solar × 7 and 3 wind × 6 |
| Plant-level parameter gates blocked | 39 | Unknown or insufficiently documented equipment-specific values |
| System-level gates blocked | 5 | Hourly availability, marginal costs, storage efficiency/SOC, transmission/interchange, independent hourly dispatch observation |
| Total blocked gates | **44** | 39 plant + 5 system |
| Screen-only slots | 0 | No scenario or reviewed-but-unvalidated inputs promoted in the current baseline |
| Empirical dispatch approved | **No** | Explicit evidence-based rejection of empirical calibration claims |

**Interpretation:** Counts are **evidence-gate outcomes for this six-site pilot**, not a failure rate for California power-system datasets, nor proof that the required parameters are unknowable. No dispatch optimization was attempted as part of this readiness check.

## Proposed manuscript Results paragraph

*The provenance-based readiness audit evaluated 39 plant-specific engineering parameter slots across six renewable pilot plants (three solar and three wind) and five system-level requirements for empirical hourly dispatch validation. All 39 plant-level slots remained blocked because the available EIA-860 generator classifications and nameplate records did not substantiate equipment-specific conversion parameters. The five system-level gates—validated plant-hour renewable availability, generator marginal costs, storage efficiency and state-of-charge constraints, network/interchange constraints, and independent hourly dispatch observations—were likewise not satisfied. The audit therefore returned 44 blocked gates and withheld empirical dispatch approval. This result describes the evidentiary limits of the assembled source stack; it does not imply that an hourly dispatch model is infeasible, nor does it evaluate dispatch performance.*

## Proposed Table R02-G1 — evidence-promotion gate

| Input class | Current evidence | Required for empirical dispatch | Decision |
|---|---|---|---|
| Technology and nameplate | EIA-860 generator-level technology and year-end nameplate | Correct vintage and plant attribution | Verified inventory context; not sufficient for dispatch |
| Solar equipment conversion | 7 unknown parameters × 3 sites | Reviewed site-specific equipment or defensible validated model | Block |
| Wind equipment conversion | 6 unknown parameters × 3 sites | Hub-height conditions, turbine curves, losses and attribution | Block |
| Renewable hourly availability | NASA POWER hourly weather; EIA-923 monthly net generation | Independently validated plant-hour availability | Block |
| Generator marginal costs | No approved cost parameter set | Fuel, efficiency and variable O&M evidence | Block |
| Storage physics | No approved storage input set | SOC initial state, energy capacity, efficiencies | Block |
| Network/interchange | No validated network constraints | Transmission capacities, topology and imports/exports | Block |
| Hourly dispatch evaluation | EIA-930 BA-level demand and incomplete fuel mix | Independent consistent hourly dispatch observations | Block |

## Scientific limitations

The readiness framework is intentionally conservative. It does not infer that every future PyPSA scenario requires all five system gates: a scenario-only simulation can use declared assumptions and has a different validation claim. This table concerns **empirical hourly dispatch validation**, which demands evidence beyond a reproducible preprocessing pipeline. The current audit is a *baseline gap inventory*, not a scored prediction of future data acquisition success.

## Remaining manuscript tasks

1. Describe the gate schema and decision rules precisely in Methods.
2. Link the 44-gate result to a source-level coverage table and missingness taxonomy.
3. Keep Figure R02-W1 as a physical plausibility example, not a dispatch validation.
4. Conduct literature review for novelty and benchmark against existing PyPSA/data validation practices.
5. Inspect the actual rendered SVG at journal dimensions; numeric audit passed but visual approval is still pending.
