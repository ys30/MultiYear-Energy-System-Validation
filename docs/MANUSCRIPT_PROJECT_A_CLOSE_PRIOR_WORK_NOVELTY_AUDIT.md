# Project A — Direct prior-work comparison and novelty risk (2026-11-10)

## Close prior work: what is already established

1. **Developing reliable hourly electricity demand data through screening and imputation** (*Scientific Data*, 2020). DOI https://doi.org/10.1038/s41597-020-0483-x. Prior study screened EIA balancing-authority demand, identified missing/anomalous values and evaluated MICE imputation. **Overlap:** EIA-930 anomaly screening and model-input quality. **Not novel here:** discovering that EIA-930 can contain anomalies; inventing a general anomaly screening procedure. **Our narrower difference:** a source-preserving, same-run *regional-net-generation versus signed fuel-category* consistency diagnostic at a specified CISO hour, integrated with an annual inventory acceptance boundary. The single five-hour case is insufficient to claim a broadly superior validation method.

2. **Catalyst Cooperative PUDL, `core_eia860m__changelog_generators`**. https://docs.catalyst.coop/pudl/en/stable/data_dictionaries/pudl_db.html. Tracks reported generator-characteristic changes across monthly EIA-860M releases, keyed by plant ID, generator ID and report date, with effective intervals. **Overlap:** longitudinal identity tracking, status changes and EIA-860 provenance. **Not novel here:** matching generator IDs over time or reporting status transitions. **Our narrower difference:** explicitly quantified 2024–2025 annual CISO OP MW accounting bridge, original year-specific Plant BA crosswalk for earlier-operating-year entrants, and linkage to downstream dispatch admission criteria. This is primarily a *case-study application*, not proof of a new changelog algorithm.

3. **NIST Technical Note 2246, Generator Fleet Characteristics Model** (2023). https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2246.pdf. Uses EIA-860 generator-level static information and EIA-930 balancing-authority time series as model inputs. **Overlap:** integration of EIA-860 and EIA-930 for electricity-system modeling. **Our narrower difference:** a documented accounting and source-quality gate prior to claiming dispatch results.

4. **Zhang, Patino-Echeverri, Li & Wu (2022), A review of publicly available data sources for models to study renewables integration in China's power system**, *Renewable and Sustainable Energy Reviews*, 159, 112215. https://doi.org/10.1016/j.rser.2022.112215. **Overlap:** evaluating completeness and reliability of public electricity-model input data. **Difference:** China-wide data-source review vs specific annual U.S. generator identity and CISO source-consistency audit.

5. **EIA official survey documentation** https://www.eia.gov/electricity/data/eia860/ and https://www.eia.gov/electricity/930-content/about.html. EIA states annual EIA-860 Operable includes operating, out-of-service and standby units; EIA-930 hourly BA data can include collection errors and revisions. These are known data semantics, not novel discoveries.

## Revised contribution claim

> We quantify the contribution of generator-record membership, reported operating status and nameplate revisions to the 2024–2025 CISO annual OP inventory change; cross-check the earlier-operating-year entrants against original year-specific Plant BA worksheets; and demonstrate a bounded, raw-source-reproducible EIA-930 cross-endpoint discrepancy. We provide a case-specific, evidence-gated interpretation of which apparent capacity changes may **not** be treated as newly commissioned or hourly available resources.

Do **not** claim first generator changelog, first EIA-930 anomaly detection, first public-data quality framework, or new PyPSA modeling algorithm.

## Reviewer-facing risk assessment

**High:** incremental novelty versus PUDL and established EIA-930 data-cleaning literature. The manuscript currently offers only one regional case, two years, and a targeted five-hour diagnostic; generalization and comparative performance are not established.

**Medium:** annual BA-filtered inventory versus operational CISO footprint; some apparent changes could reflect reporting scope. Plant-sheet comparison only covers earlier-year entrant subgroup.

**Medium:** journal fit. The work currently resembles a focused reproducibility/validation case study or technical data note more than a broad methodological advance.

**Low for arithmetic, high for causal interpretation:** the bridge reconciles exact MW totals, but class membership does not establish physical construction, retirement, or operational capability.

## Suggested manuscript edits

- Introduction: acknowledge PUDL generator changelogs and existing EIA-930 anomaly screening explicitly.
- Discussion: explain that the contribution is **an empirical accounting case with explicit evidence gates**, not a novel record-linkage method.
- Limitations: emphasize the 2024–2025 CISO-only design and five-hour targeted diagnostic.
- Before submission: compare results against PUDL monthly changelog where feasible, or explain why such a comparison is outside the scope. Do not claim validation against PUDL unless run.
