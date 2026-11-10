# Project A — Discussion, limitations and contribution audit (private draft)

**Status:** draft for methodological manuscript. No new experimental result is claimed here. The paper is about reproducible evidence-gated data validation; calibrated empirical PyPSA dispatch has not been performed.

## 4. Discussion

### 4.1 Reproducible ingestion is necessary but not sufficient for credible simulation

The principal finding of this case study is a distinction between **source fidelity** and **modeling admissibility**. Reconstructing EIA generator inventories, monthly generation, balancing-authority load and meteorological inputs in a reproducible workflow does not imply that the resulting records can directly parameterize hourly power-system dispatch. The sources describe different entities and physical quantities: generator nameplate is not delivered energy; plant–fuel monthly net generation is not a plant-hour availability series; and gridded 10-m wind is not a calibrated hub-height power input. A provenance-aware workflow can preserve these differences rather than silently bridging them through unreported assumptions.

In the six-site baseline, the readiness audit blocked 39 plant engineering parameter slots and five system-level requirements. This **44-gate count** quantifies the evidence missing under the *specific conservative policy implemented here*. It is not an intrinsic physical dimension of the California grid, a comparison of model accuracy, or a universal minimum parameter count for PyPSA. In particular, a transparent scenario model may use assumptions that would be inadmissible for a claim of **empirically validated hourly dispatch**.

### 4.2 Temporal comparison design changes the apparent strength of physical agreement

The three wind plants showed substantially different within-year correlations between monthly mean NASA POWER 10-m wind speed and observed daily-normalized EIA-923 generation. These differences were less pronounced when the comparison was reformulated as paired same-calendar-month year-over-year changes. The finding is not that one correlation estimator is categorically superior; rather, the estimand changes. Within-year correlations combine resource variation, seasonal demand/curtailment, maintenance schedules and potential operating-capacity changes. Same-month interannual contrasts partially control for recurring calendar-month patterns, but with only two years they cannot identify causal weather effects or eliminate time-varying operational confounding.

The leave-one-month-out analysis assesses sensitivity to influential observations; it is **not** a confidence interval, cross-validation of a forecasting model, or evidence of temporal generalization. Strong correlations for plants 57514 and 7526 should not be read as calibrated power curves. Plant 7526's 2024 commissioning history further cautions against interpreting annual year-end nameplate as uniform monthly operating capacity.

### 4.3 Evidence gates as a reproducible research object

A useful contribution of the pipeline is that *refusal to promote an unsupported input* becomes a testable and archived output. Each plant parameter begins unknown. Documented plant-specific updates require a traceable source locator, applicable equipment/vintage and a reviewer; scenario assumptions retain their own label. Separate system-level gates prevent an isolated documented parameter from being mistaken for end-to-end empirical readiness. The generated JSON report allows later reviewers to identify which evidence is missing and to repeat the same decision policy.

This approach supports transparent failure analysis and reproducibility, but the current gate implementation is **conservative and incomplete**. The five system-level gates are currently explicit baseline requirements marked unverified, rather than a dynamic inventory that discovers every possible data source and evaluates all available evidence. Consequently, the observed 44 blocked gates demonstrate correct behavior under a predefined evidence policy, not an empirical measurement of the complete universe of data gaps. A future extension should define applicability by model scope and distinguish evidence absence, failed validation, and nonapplicability.

### 4.4 Positioning relative to open energy-system modeling practice

Open-source modeling frameworks, including PyPSA, provide mechanisms to represent networks, generators, storage and time-dependent dispatch constraints. The present workflow should **not** claim that provenance tracking, data validation, or scenario separation is novel in general. Its narrower potential contribution is an executable, source-aware evidence-promotion layer for a concrete two-year U.S. data stack, coupled to explicit simulation-readiness outputs and traceable descriptive physical diagnostics.

A formal novelty claim requires a systematic comparison with existing PyPSA-Eur/PyPSA-USA preprocessing, validation, scenario assumptions, and model evaluation practices. Until that review is complete, phrase novelty as **an implemented case-study workflow**, not *the first* evidence-gated energy model or a demonstrated improvement over prior pipelines.

### 4.5 Implications for model users

The results suggest a practical distinction among three outputs: (i) an auditable source-aligned dataset; (ii) exploratory physical/resource diagnostics; and (iii) empirically validated dispatch. The first two were demonstrated within the pilot. The third was withheld because required plant-hour, cost, storage, network and independent validation inputs were not substantiated. A defensible next step is to prioritize evidence acquisition by the decision being supported, rather than to substitute synthetic defaults and report the resulting optimization as an empirical validation.

### 4.6 Limitations and threats to validity

**External validity:** six selected sites do not represent all CISO generators, technologies or regions. The 2024–2025 comparison is limited to three wind plants and two years.

**Measurement validity:** NASA POWER WS10M is a gridded near-surface wind estimate; EIA-923 generation is plant–fuel-level monthly output, affected by operational and reporting factors. Neither is a direct measure of hourly turbine availability.

**Temporal validity:** leap-year normalization addresses month length but not time-zone conventions, within-month commissioning, or plant-hour curtailment. A monthly analysis cannot resolve hourly operational dynamics.

**Statistical validity:** Pearson r with 12 observations is sensitive to seasonality and influential months. LOMO ranges are descriptive sensitivity checks and are not uncertainty intervals. No hypothesis test, out-of-sample validation or causal identification is asserted.

**Decision-rule validity:** the 44-gate baseline reflects a predefined conservative audit; no independent expert benchmark yet establishes that the exact gate list is optimal or exhaustive. The current implementation should not be described as automatically discovering the presence or absence of every potentially relevant data source.

**Figure validation:** 21 SVG-to-JSON numeric checks and SVG-specific tests passed in CI, but journal-size visual review is still pending.

## 5. Conclusion — draft

This study demonstrates a reproducible, evidence-gated workflow for assembling and assessing heterogeneous U.S. electricity and weather records across 2024–2025. In a six-site pilot, source-aware audits preserved distinctions between capacity, observed monthly output, hourly system demand and meteorological resource proxies. Wind-resource/generation associations varied with the temporal contrast, illustrating the need to specify the comparison design before drawing physical conclusions. An executable readiness audit withheld empirical hourly dispatch approval when 39 plant parameter slots and five system-level requirements lacked sufficient evidence. These results establish a traceable validation boundary, not a calibrated dispatch model or evidence of improved optimization accuracy. The principal next step is to acquire independently validated operational inputs and test whether evidence-gated preprocessing improves downstream model evaluation relative to explicit baseline practices.

## Required next work before submission

1. Verify and cite primary literature on PyPSA, PyPSA-USA, PyPSA-Eur and energy-data validation; create a claim-by-claim novelty matrix. Do not invent references.
2. Specify system-gate applicability and distinguish *missing*, *unverified*, and *not applicable* in a next-version audit.
3. Create a source coverage/failure-mode table with verified numerators and denominators.
4. Conduct actual journal-size SVG inspection and update Figure R02-W1 acceptance.
5. Integrate Methods, Results, Discussion, conclusion and cited bibliography into a complete manuscript only after the above checks.
