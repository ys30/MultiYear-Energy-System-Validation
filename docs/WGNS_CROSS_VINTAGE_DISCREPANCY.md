# WGNS: cross-vintage annual versus monthly reporting discrepancy

## Verified evidence (plant 50535, generator WGNS)

| Dataset | Reporting vintage | Source worksheet | Status | Nameplate MW | Operating date | Retirement date |
|---|---|---|---|---:|---|---|
| EIA-860 annual | 2023 | Retired and Canceled | RE | 27 | 1984-11 | 2020-12 |
| EIA-860M monthly | 2023-12 | Retired | Retired-sheet classification | 27 | 1984-11 | 2020-12 |
| EIA-860M monthly | 2024-12 | Retired | Retired-sheet classification | 27 | 1984-11 | 2020-12 |
| EIA-860 annual | 2024 | Operable | OP | 33.6 | 1984-11 | not present in extracted fields |

The monthly December 2024 record **does not corroborate** the annual 2024 OP / 33.6 MW entry. These datasets have different publication and revision processes. Do not infer a physical restart or a timestamp for any administrative change.

## Reproducible official monthly sources

- [December 2023 XLSX](https://www.eia.gov/electricity/data/eia860m/archive/xls/december_generator2023.xlsx) — SHA-256 `cb23a95036f99ad6f43c756c5c7d050953337149a452291760240abf881ebf00`
- [December 2024 XLSX](https://www.eia.gov/electricity/data/eia860m/archive/xls/december_generator2024.xlsx) — SHA-256 `22c742b72fd7709d4632a92074fa968cc5a728b9c8f0cbc82959b327e0eba8e7`

The independent source inspection ran successfully in GitHub Actions run [44449378102](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44449378102).

## Evidence needed to resolve

1. Identify the EIA-860 annual 2024 release vintage, any revision notes, and reporting definitions relevant to retired versus operable status.
2. Check the intervening 2024 monthly EIA-860M snapshots and later revisions for a change in the reported WGNS row; report **first observed dataset vintage**, not physical commissioning date.
3. Seek independent operator / regulatory evidence for physical identity or status.
4. Keep the historical generator-to-target identity mapping and empirical PyPSA dispatch gate **unapproved** until independent verification.

## Paper-ready cautious finding

> For plant 50535, generator WGNS, the December 2023 and December 2024 EIA-860M monthly snapshots both report the generator on the retired worksheet with 27 MW nameplate capacity and a December 2020 retirement date. In contrast, the 2024 EIA-860 annual workbook reports the same generator key as operable (OP) with 33.6 MW. This cross-vintage disagreement illustrates the risk of treating reported annual inventory transitions as physical commissioning or retirement events without independent validation.

## 2024 quarterly monthly-vintage follow-up (verified)

GitHub Actions [44453709385](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44453709385) successfully inspected five official monthly snapshots: December 2023 and March, June, September and December 2024. Every inspected snapshot independently located plant 50535 / generator WGNS on the **Retired** sheet, with **27 MW** nameplate capacity, operating date **November 1984**, and retirement date **December 2020**.

| Monthly vintage | Official workbook SHA-256 | WGNS sheet | Nameplate MW | Retirement |
|---|---|---|---:|---|
| 2024-03 | `5002bff3d163cbf540f904431c48269005ec6f0880d633cbe969299d7107d3cc` | Retired | 27 | 2020-12 |
| 2024-06 | `19fd9395da97d257c40b86fd976d0675088a902e3e6243f10e8dddfd960f5ea1` | Retired | 27 | 2020-12 |
| 2024-09 | `b8f123c4b8655ba384b88d4326527541c435ec46257b265c83fa1b5445fe0df9` | Retired | 27 | 2020-12 |
| 2024-12 | `22c742b72fd7709d4632a92074fa968cc5a728b9c8f0cbc82959b327e0eba8e7` | Retired | 27 | 2020-12 |

Official monthly URLs follow the verified pattern
`https://www.eia.gov/electricity/data/eia860m/archive/xls/{month}_generator2024.xlsx`.
These are **four sampled monthly vintages**, not an exhaustive review of all twelve months. No observed change across these samples establishes neither that every intervening month was identical nor when the annual workbook's different reported status first appeared.

**Revised paper interpretation:** Four independent 2024 quarterly EIA-860M snapshots consistently list WGNS as retired (27 MW, retirement December 2020), whereas the 2024 annual EIA-860 lists the same key as OP (33.6 MW). The divergence is between source vintages/products and must not be described as proven physical recommissioning.
