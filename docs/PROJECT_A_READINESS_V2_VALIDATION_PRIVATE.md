# Project A — evidence-gate v1/v2 validation and manuscript integration (private)

**Verified CI:** [R02 six-site extended physical weather #42877232149](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42877232149), successful on commit `728b41d0`.

## Verified audit output

| Measure | v1 | v2 |
|---|---:|---:|
| Pilot plants | 6 | 6 |
| Engineering parameter slots | 39 | 39 |
| System-level requirements | 5 | 5 |
| Total blocked gates | 44 | 44 |
| Screen-only gates | 0 | 0 |
| Explicitly not-applicable gates | Not separately represented | 0 |
| Empirical dispatch approved | No | No |

The v2 JSON emits `decision_counts={"block":44,"not_applicable":0,"screen_only":0}`, `total_gates=44`, `plant_count=6`, and `empirical_dispatch_approved=false`. The corresponding v1 audit reported 44 blocked gates and zero screen-only gates. Figure R02-W1 independently passed 21 SVG-to-source numeric checks in the same run.

## Methods insert: versioned evidence-state audit

The baseline audit (v1) assigned each plant-specific engineering parameter and each system-level empirical-dispatch requirement a conservative decision of blocked or screen-only. Version 2 retained the same plant and system inventory but explicitly separated **evidence state** from **modeling decision**. System-level evidence states are *missing*, *unverified*, *validated* and *not_applicable*. The not-applicable state is permitted only when a corresponding model-scope declaration explicitly excludes the requirement; it cannot be used to relabel a missing but applicable input. A validated claim requires source title, URL, locator, equipment applicability, effective year and reviewer. Individual documented or validated inputs remain screen-only pending independent end-to-end review, rather than automatically approving empirical hourly dispatch. For plant engineering parameters, the current implementation distinguishes missing values and unverified scenario/documented values; it does **not yet implement an independent plant-level validated decision state**. This asymmetry must be described accurately.

The v2 baseline is deliberately conservative: no site engineering parameter or system-level gate was promoted. The resulting decision counts reproduce the v1 blocked total, showing **backward compatibility on this baseline**, not validation of all possible model scopes.

## Results insert: audit compatibility and scope control

The applicability-aware v2 audit reproduced the v1 baseline outcome across the six pilot plants: 39 engineering parameter slots and five system-level requirements were blocked, yielding 44 blocked gates and zero screen-only or not-applicable decisions. Empirical dispatch approval remained withheld. Additional contract tests verified that unsubstantiated validated claims are rejected and that a system-level not-applicable state requires an explicit scope declaration. These tests demonstrate the intended control logic under synthetic test inputs; they do not establish that the full inventory of real-world evidence has been independently reviewed.

## Proposed reviewer-facing interpretation

The principal contribution is a machine-readable, auditable separation of (i) evidence availability, (ii) model-scope applicability and (iii) permission to claim empirical validation. A successful source-ingestion workflow is not itself proof that all downstream physical and economic model inputs are empirically supported. The audit makes this boundary explicit without asserting that scenario-based PyPSA analysis is invalid.

## Technical caveats requiring resolution before submission

1. **System evidence is externally supplied, not discovered automatically.** Missing entries default to missing; a validated claim currently passes metadata checks but not independent verification of the source's content.
2. **Applicability declarations are assertions, not independently justified.** Add a reviewer and rationale requirement for each not-applicable system gate before relying on scope exemptions in a paper.
3. **Plant-level validated status is not independently implemented.** Documented plant-specific inputs remain screen-only. Do not claim that v2 supports full plant-level validation.
4. **Dispatch approval is always false by design.** The current code is a fail-closed audit, not a workflow that can automatically promote a completed empirical model. This is appropriate for the current baseline but limits claims about a complete evidence-to-approval lifecycle.
5. **Backward compatibility is established only for this baseline**; test additional synthetic scope/evidence combinations before claiming general compatibility.
6. **Figure numeric checks do not replace visual inspection** at target journal size.

## Next implementation step

Add explicit scope rationale/reviewer metadata for not-applicable gates, and reject unsupported exclusions; then run CI and update the paper to describe only the verified behavior.
