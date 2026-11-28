# Paper A1: national cross-vintage generator consistency — preregistered analysis protocol (draft)

Status: **design frozen for implementation; no national results claimed**. This document separates established Mesa Wind evidence from proposed nationwide analyses. It does not authorize empirical PyPSA dispatch or generator crosswalks.

## Research question and contribution

**RQ1** How frequently do generator-level identifiers, capacity, and operating status disagree across EIA-860 annual releases, EIA-860M monthly snapshots, and the pinned PUDL annual release?

**RQ2** How do conservative, provenance-preserving identity decisions compare with PUDL's published entity-resolution outputs? Distinguish verified continuity, documented repowered successor, candidate, conflict, and unresolved. Do not treat PUDL's canonical IDs as ground truth.

**RQ3** What is the downstream impact of unresolved records on yearly capacity and retirement/entry summaries? A separate, explicitly approved stage may quantify PyPSA dispatch effects only after operational data and identity evidence pass independent review.

## Source and cohort freeze

- National population: all generator records in the pinned **PUDL v2026.11.0** yearly generator parquet, report years **2023, 2024, 2025**. Keep the full population; the 29 targets are an enriched diagnostic subset, not a prevalence sample.
- Independent official source: archived EIA-860 annual 2023, 2024, 2025 generator records; EIA-860M archived monthly snapshots for cases where relevant. Record official URL, retrieval date, archive SHA-256, table/sheet and row locator.
- Freeze the source versions and field dictionary before computing prevalence. Explicitly separate **report year** from **publication vintage** and **reported operating/retirement dates**.
- Unit of observation: (source product, source vintage, report year or month, plant_id_eia, generator_id). A record may have multiple versions. Avoid silently deduplicating them.
- Universe denominators: source-specific plant/generator records and unique plant IDs; report each denominator. Missing records are **coverage differences**, not automatically errors, closures, or newly commissioned units.

## E1: national cross-source consistency

Produce a reproducible, machine-readable exception ledger and source-specific counts by year, technology, capacity band and operating status. Mutually exclusive top-level classes: exact agreement, attribute conflict, ID discontinuity, source-only record, and unresolved/insufficient evidence. Record secondary flags (e.g., multiple simultaneous conflicts) separately. Report absolute counts, rates with denominators, MW-weighted summaries and Wilson 95% confidence intervals only when the sampling/estimand warrants inference. Nationwide census results should be described as descriptive population statistics, not inferential estimates.

For every cross-vintage difference distinguish: (a) revisions of the same record; (b) source/product timing differences; (c) evidence of replacement/repower; (d) unresolved. **Never label a discrepancy as an EIA error without independent corroboration.**

## E2: identity validation and baselines

Compare: B0 exact (plant_id_eia, generator_id) match; B1 published PUDL canonical/entity-resolution outputs when available; B2 conservative evidence gate requiring primary generator-level lineage, explicit relationship and source locator. B2 may abstain. Construct a stratified, independently reviewed validation sample across agreement, ID change, source-only and conflicting-status categories; record selection probabilities and reviewer decisions. Use blinded dual review with adjudication where feasible. Report precision/recall conditional on adjudicated cases, false-link rate, abstention/coverage rate, and disagreements; show sensitivity to unresolved labels. Do not use automatic match outputs as reference truth.

## E3: vintage revision chronology

For a pre-specified set of ambiguous plants, compare monthly and annual snapshots. Record first **observed reporting** transition, never infer physical commissioning from first observation. Mesa Wind (plant 50535, WGNS/MWD1) is an explanatory case, not the only result and not proof of a physical crosswalk.

## E4: consequences for capacity and modeling

Calculate lower/upper capacity totals and entry/retirement timelines under: exact-only, verified lineage, and conservative unresolved-exclusion scenarios. Do not add capacities for ambiguous apparent successors without defensible identity evidence. Report MW and percent difference by region/year/technology. Any PyPSA simulation is a later gated stage requiring validated load, generation and operational dates; otherwise report **input sensitivity only**.

## Quality and publication gates

1. Pin source archives and SHA-256; confirm parser and schema invariants in CI.
2. National E1 tables reconcile to input record counts, and all exception categories are exhaustive.
3. Validation sample and independent adjudication support E2 claims.
4. Reproduce E3 source-vintage timelines with immutable provenance.
5. E4 sensitivity calculations document treatment of unresolved units and prohibit double counting.
6. Separate **observed evidence**, **hypotheses**, and **model assumptions** in manuscript and supplementary files.
7. Do not report nationwide discrepancy prevalence, algorithm superiority, or PyPSA effects until corresponding computations actually finish.

## Manuscript structure

Introduction (known PUDL entity-resolution work and EIA preliminary revision caveats); Data and version provenance; E1–E4 Methods; National prevalence and identity validation Results; Mesa Wind case study; Downstream capacity implications; Limitations and reproducibility. Position the contribution as **vintage-aware uncertainty-preserving validation**, not invention of entity resolution or discovery that monthly data are revised.

## Current evidence boundary (2026-11-21)

The prior 29-target diagnostic found 0/29 exact matches in 2023 and 2024, 29/29 in 2025, with five historical IDs across four plants; this **cannot** estimate nationwide error prevalence. Official Mesa Wind monthly snapshots show a WGNS reporting-status transition first observed in May 2025 and no exact MWD1 monthly ID in 2025; annual/monthly disagreement remains unresolved. The generator identity gate disallows physical crosswalk and empirical dispatch. Latest CI status must be checked independently; no success is presumed.
