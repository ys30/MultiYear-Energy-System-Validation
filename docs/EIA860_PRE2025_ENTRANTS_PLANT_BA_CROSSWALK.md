# Project A: 2024–2025 EIA-860 plant-level BA crosswalk for pre-2025 entrants

**Verified on 2026-11-10 from actual annual EIA-860 Plant worksheets, not inferred from generator transition summaries.** Downloaded private GitHub Actions source archives: 2024 artifact **13281394181** and 2025 artifact **13282152290** (run [41743257455](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41743257455)); generator transition artifact **13295023796** (run [41772668659](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41772668659)). Parsed `2___Plant_Y2024.xlsx` and `2___Plant_Y2025.xlsx`, `Plant` sheets, matching exact `Plant Code` and `Balancing Authority Code` for all 20 plants containing 29 pre-2025-operating-year entrants, plus pumped-storage plant 6100.

## Crosswalk result

| Source-level classification | Distinct plants | Generator entrants | 2025 OP MW |
|---|---:|---:|---:|
| Plant present in 2024 and 2025, BA=CISO both years | **4** | **6** | **103.6** |
| Plant absent from 2024 Plant worksheet, present in 2025 with BA=CISO | **16** | **23** | **34.5** |
| **Total** | **20** | **29** | **138.1** |

The 4 already-CISO plants are **50535 Mesa Wind Power LLC, 61446 RE Gaskell West 2 LLC, 63094 Santa Barbara ReSource Center, 65820 Ocotillo Wells**. Their entrant generator records are newly present within an **already-CISO plant**; they cannot be explained by a 2024→2025 change of the plant-level BA code.

The other 16 plant IDs are **58472, 69114, 69132, 69190, 69191, 69288, 69363, 69563, 69856, 69898, 69899, 70039, 70173, 70174, 70383, 70434**. These plant IDs were **absent from the 2024 Plant worksheet**, not merely observed with a different BA code. Thus this source comparison does **not** establish an observed BA reassignment. They are present in 2025 with BA=CISO; historical operating years could reflect delayed entry, reporting scope or other changes. Their 23 generator records include non-OP statuses; OP contribution is 34.5 MW.

## Pumped-storage falsification check

Plant **6100, Helms Pumped Storage**, has **BA=CISO in both 2024 and 2025 Plant worksheets**. Its three generators (1, 2, 3), 351 MW each, report **June 1984** operating dates in both generator-year records and status **OA→OP**. Consequently the +1,053 MW OP inventory delta is a status reclassification within a consistently CISO-assigned plant, **not** a plant-level BA reassignment or verified 2025 construction.

## Limitations and remaining checks

- Plant absence in an annual worksheet does not establish plant nonexistence, physical construction, or a specific administrative cause.
- BA=CISO in both annual worksheets is a year-specific plant-code observation, not validation of the operational/electrical CISO boundary or hourly interchange.
- This crosswalk covers the **29 earlier-operating-year entrant records** and plant 6100, not all 157 entrants or all CISO generators.
- To explain the 16 absent-then-present plants, inspect plant registration, ownership and reporting histories in independent primary sources; for the 4 already-CISO plants, check generator IDs and generator-sheet status/operating dates.
- **Empirical dispatch remains BLOCKED** pending hourly availability, interchange, storage MWh, costs and boundary verification.

**No new dispatch simulation was performed.**
