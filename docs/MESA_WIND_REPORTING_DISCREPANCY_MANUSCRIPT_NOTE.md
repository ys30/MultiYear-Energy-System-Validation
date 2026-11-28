# Mesa Wind reporting-vintage discrepancy: manuscript-ready evidence note

**Scope.** This note addresses the reported generator status and nameplate capacity of WGNS at EIA plant 50535, rather than inferring physical commissioning or generator lineage. The analysis triangulates official annual EIA-860, archived monthly EIA-860M, and pinned PUDL annual generator keys. Monthly source files were downloaded directly from EIA and hashed in CI.

## Findings

1. The official **2023 annual EIA-860** classifies WGNS as retired (RE), nameplate 27 MW, retirement December 2020, and historic operating date November 1984.
2. All **12 archived monthly 2024 EIA-860M** workbooks classify WGNS in the Retired sheet at 27 MW. However, the **2024 annual EIA-860** reports WGNS as operating (OP) at 33.6 MW, retaining November 1984 as its operating date. These two official products disagree about the same reporting year.
3. All **12 archived monthly 2025 EIA-860M** workbooks were successfully retrieved and parsed in strict CI [run 44787027792](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44787027792). WGNS is Retired/27 MW in January–April and Operating/33.6 MW in May–December. Thus **May 2025 is the first observed monthly snapshot of the changed classification**, not a verified date of physical commissioning.
4. The official **2025 annual EIA-860** contains MWD1 as operating (OP), 30 MW, with reported operating month June 2024. MWD1 is not an exact generator-ID match in any of the twelve inspected 2025 monthly workbooks. Absence from a particular data product is not evidence of physical absence.
5. Independently documented Mesa Wind repowering supports the existence of a physical repower project, but the reviewed sources **do not establish that WGNS and MWD1 are the same physical generator**. The 33.6 MW WGNS nameplate, 30 MW MWD1 nameplate, and 30 MW interconnection limit should not be conflated.

## Suggested manuscript results paragraph

> At EIA plant 50535 (Mesa Wind), we identified a cross-product discrepancy in generator reporting. The 2024 annual EIA-860 classified generator WGNS as operating with 33.6 MW of nameplate capacity, whereas all twelve archived 2024 monthly EIA-860M snapshots retained WGNS in the retired category at 27 MW. In the 2025 monthly series, WGNS remained retired at 27 MW through April and was first listed as operating at 33.6 MW in May; this classification persisted through December. The 2025 annual EIA-860 separately listed generator MWD1 as operating at 30 MW, with a reported operating date of June 2024, although MWD1 was not identified in any of the twelve 2025 monthly snapshots. These differences demonstrate that generator identity and reported operating status cannot be reconstructed reliably by equating publication date, annual and monthly status fields, or plant-level capacity. They do not, by themselves, establish the physical commissioning date or a WGNS–MWD1 identity crosswalk.

## Suggested limitations paragraph

> Our evidence describes official reporting snapshots rather than independently observed equipment operations. We did not locate a primary-source generator-level lineage record linking WGNS to MWD1 or a verified EIA correction history explaining the 2024 annual/monthly disagreement. Consequently, we treat the apparent May 2025 monthly change as a reporting transition, do not infer a physical restart, and exclude this unresolved generator lineage from empirical dispatch reconstruction pending additional verification.

## Provenance and reproducibility

- [Full-year 2025 monthly evidence, source URLs and SHA-256](MESA_WIND_REPOWER_INDEPENDENT_EVIDENCE.md)
- [2024 annual versus monthly discrepancy and 13 archived monthly checks](WGNS_CROSS_VINTAGE_DISCREPANCY.md)
- [Generator identity triangulation matrix](MESA_WIND_GENERATOR_IDENTITY_TRIANGULATION.md)
- [Official annual crosscheck plan](OFFICIAL_EIA860_ANNUAL_SOURCE_CROSSCHECK_PLAN.md)
- [Strict 2025 monthly CI run](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44787027792)

**Model gate:** physical commissioning verified = false; generator identity crosswalk verified = false; empirical PyPSA dispatch approved = false.
