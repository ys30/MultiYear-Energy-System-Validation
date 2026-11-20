# Mesa Wind (EIA plant 50535): generator identity triangulation

Status: evidence audit; **no physical generator-ID crosswalk accepted**. This table distinguishes the date of a *published snapshot* from a reported equipment operating date.

| Evidence product / vintage | WGNS | MWD1 | What the evidence supports |
|---|---|---|---|
| Official EIA-860 annual 2023 | RE; 27 MW; reported retired Dec 2020; original operating date Nov 1984 | Not established by this annual source | Historic WGNS record |
| Official EIA-860M monthly Jan–Dec 2024 (12 archived files) | Retired sheet; 27 MW in all 12 | Not independently established | All 2024 monthly archives retain the retired classification |
| Official EIA-860 annual 2024 | OP; 33.6 MW; operating date Nov 1984 | No exact 2024 target key in the pinned annual PUDL comparison | Cross-product/vintage discrepancy with monthly 2024 |
| Official EIA-860M monthly Jan–Apr 2025 (4 archived files) | Retired sheet; 27 MW | No exact ID in sampled monthly files | Last observed retired snapshot: April 2025 |
| Official EIA-860M monthly May–Jun 2025 | Operating sheet; 33.6 MW | No exact ID in sampled monthly files | First observed operating snapshot: May 2025 |
| Official EIA-860M monthly Dec 2025 | Operating sheet; 33.6 MW | No exact ID in sampled monthly file | Reported operating status persists in December |
| Official EIA-860 annual 2025 | Annual WGNS classification not established here | OP; 30 MW; reported operating June 2024 | Annual MWD1 record; **not** evidence of WGNS-to-MWD1 identity |
| Pinned PUDL annual parquet v2026.11.0 | Historical WGNS observed in 2023/24 | MWD1 observed as a 2025 target | PUDL key differences across years; not an asset lineage |

Sources and reproducibility:
- 2025 monthly hashes and workbook URLs: [independent evidence audit](MESA_WIND_REPOWER_INDEPENDENT_EVIDENCE.md), [verified CI run 44762285158](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44762285158).
- 2024 monthly and annual discrepancy: [cross-vintage audit](WGNS_CROSS_VINTAGE_DISCREPANCY.md).
- Official annual source crosscheck: [annual audit plan](OFFICIAL_EIA860_ANNUAL_SOURCE_CROSSCHECK_PLAN.md).
- Independent repowering project evidence: [independent evidence audit](MESA_WIND_REPOWER_INDEPENDENT_EVIDENCE.md).
- Full 2025 12-month extension has been submitted but **is not yet validated**; July–November must not be marked as observed until CI succeeds.

## Competing explanations, not findings

1. **Reporting vintage / retrospective corrections:** annual 2024 OP/33.6 and 2024 monthly Retired/27 disagree. A reporting revision could explain this, but no correction notice or data lineage has been verified.
2. **Repower asset registration / ID reassignment:** an old generator record and a repowered unit may be represented differently across products. The project repower is independently documented, but the specific WGNS–MWD1 physical mapping is unverified.
3. **Capacity definition differences:** 33.6 MW nameplate, 30 MW annual MWD1 nameplate and a 30 MW interconnection limit must not be treated as interchangeable quantities.

## Evidence required to resolve identity

- Official EIA generator-level change records, EIA-860 schedule metadata, or a plant/operator confirmation explicitly relating WGNS and MWD1.
- A documented correction/version history explaining annual 2024 vs monthly 2024 and the April–May 2025 monthly classification change.
- Independent commissioning or operational evidence tied to a *specific* generator ID, not merely to plant 50535.

## Model gate

Until generator lineage, commissioning and time-indexed capacity are independently reconciled, **do not splice WGNS into MWD1, do not backfill a 2024 commissioning event from a 2025 publication, and do not approve empirical PyPSA dispatch on this inferred identity**. The 2025 monthly transition is a reporting observation, not a physical commissioning date.
