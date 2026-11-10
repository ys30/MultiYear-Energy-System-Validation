# Project A paper architecture and evidence-to-claim matrix (private)

**Status:** writing plan, not a finished manuscript or empirical dispatch validation. Updated 2026-11-10.

## Recommended manuscript focus

**Working title:** *An evidence-gated, multi-year data validation framework for reproducible regional power-system modeling: a California case study.*

The contribution is a reproducible **validation and provenance workflow** before simulation, not a claim that calibrated hourly PyPSA dispatch has already been achieved. The three-plant wind study is an illustrative physical plausibility diagnostic rather than the main power-system result.

## Proposed research questions

1. **RQ1 — temporal and source integrity:** Which errors and ambiguities arise when combining EIA-860 generator inventories, EIA-923 observed monthly generation, EIA-930 balancing-authority hourly demand, and NASA POWER weather across 2024–2025?
2. **RQ2 — evidence promotion:** Which quantitative and provenance gates must be met before a plant attribute is promoted from screening evidence to a PyPSA simulation parameter?
3. **RQ3 — robustness of descriptive validation:** How does the apparent agreement between wind-resource proxies and observed generation change across within-year, leave-one-month-out, and matched-month interannual designs?
4. **RQ4 — operational readiness:** Which missing inputs prevent empirical hourly dispatch validation, despite successful reproducible data assembly?

## Evidence-to-claim matrix

| Claim | Evidence | Allowed interpretation | Disallowed leap |
|---|---|---|---|
| Two-year source integration is reproducible | Versioned EIA/NASA workflows, contract tests, R02 CI | Reproducible source-aware preprocessing | Fully validated power-system model |
| Hourly demand records have nontrivial anomalies and fuel coverage gaps | EIA-930 screening (2025 July 31 CISO demand anomaly; 2024 Nov 2–3 missing fuel hours) | Missingness/anomaly flags are needed | Imputations are verified observations |
| Plant selection and commissioning affect representativeness | EIA-860 six-site audit, Bellefield post-July 2025 commissioning | Screen before observational comparison | Six sites represent all CISO generation |
| Wind-speed/generation association depends on comparison design | Three wind plants, 2024–2025 monthly EIA-923/NASA POWER; Figure R02-W1 | Descriptive temporal-association sensitivity | Hub-height power curve, causal attribution, forecast skill |
| SVG numeric provenance is reproducible | CI #42851314978; 21 JSON-to-SVG numeric checks | Figure coordinates match analytical JSON | Statistical validity beyond the inputs |
| Empirical hourly PyPSA dispatch is not yet validated | Parameter evidence gates and missing input inventory | Clear, auditable readiness boundary | Calibrated dispatch, reliability or cost conclusions |

## Draft paper structure

1. **Introduction:** multi-source temporal and physical consistency is a prerequisite for credible open energy-system simulation; identify the methodological gap without claiming novelty unsupported by literature review.
2. **Data and provenance:** source/version tables; CISO scope; leap-year and time-zone normalization; missingness taxonomy; generator commissioning and plant-fuel attribution.
3. **Methods:** source contracts, evidence promotion gates, physical plausibility diagnostics, temporal contrast definitions, and a formal simulation-readiness decision.
4. **Results:** (a) source coverage and failure modes; (b) commissioning/representativeness audit; (c) wind 2024–2025 descriptive association Figure R02-W1; (d) simulation readiness gates and blocked parameters.
5. **Discussion:** reproducibility versus empirical validity; plant-level representativeness; why 10-m wind and monthly net generation cannot yield hourly capacity factors; limitations and transferable use.
6. **Conclusion:** what the pipeline verifies, what it rejects, and what additional evidence is needed for dispatch.

## Suggested figures/tables (avoid redundant plots)

- **Fig. 1:** provenance and evidence-promotion workflow (planned).
- **Fig. 2:** multi-source temporal coverage and failure-mode heatmap (requires explicit source-level counts).
- **Fig. 3:** Figure R02-W1 wind association (numeric audit passed; manual visual review pending).
- **Table 1:** source temporal resolution, authority, coverage and known limitations.
- **Table 2:** evidence-to-parameter promotion matrix with pass/block reasons.
- **Table 3:** wind comparison estimates and LOMO ranges, if not redundant with Fig. 3.

## Next concrete analysis

Generate a **machine-readable simulation-readiness report** from existing parameter evidence gate outputs: parameter, source, temporal resolution, required resolution, observed validation status, decision (pass/screen-only/block), and rationale. Do not substitute synthetic defaults for empirical readiness. Add contract tests for blocking missing availability, storage SOC/efficiency, generator costs, and transmission/interchange.

## Figure R02-W1 acceptance

As of run #42851314978, the SVG-specific pytest step and independent 21-value JSON-to-SVG audit both passed. The plot is a **candidate** until its actual rendered layout has been inspected at manuscript sizes and cross-references finalized.
