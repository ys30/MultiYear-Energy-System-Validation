# Project A — Historical generator ID review (2023–2024)

Source: pinned PUDL `v2026.11.0`, `out_eia__yearly_generators.parquet`. Verified in GitHub Actions run https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44242038951. Fixed target list: `data/pudl/project_a_pudl_29_targets.csv`.

## Historical rows and 2025 target IDs at the same plant

| EIA plant | Historical IDs in **both** 2023 and 2024 | 2025 cohort target IDs | Exact overlap |
|---|---|---|---|
| 50535 | WGNS | MWD1 | None |
| 61446 | PV2 | BA2 | None |
| 63094 | SBAD1, SBAD2 | G100, G200, SOLAR | None |
| 65820 | OWS | OWB | None |

Historical annual generator records: **5 in 2023** and **5 in 2024** across these four plants. The target cohort contains **6 different generator IDs** at these plants, none matching the historical IDs. This does **not** establish that an ID was renamed, that two records refer to the same physical unit, or that a target generator was absent before 2025.

## High-priority independent review

1. Compare official **2023 and 2024 EIA-860 annual** generator records for each plant and all generator IDs above, preserving raw source filenames, reporting years, statuses, operation dates and SHA256 hashes.
2. Review official 2025 EIA-860 generator records for the six target IDs. The fixed target cohort lists reported operating years 2021–2024, so a 2025-only appearance in this PUDL annual table must **not** be interpreted as 2025 commissioning.
3. Do **not** infer `WGNS→MWD1`, `PV2→BA2`, `SBAD1/SBAD2→G100/G200/SOLAR`, or `OWS→OWB` without independent plant-level documentary evidence.
4. Review the remaining 23 historical unmatched targets separately: their plants have no generator records in the 2023/2024 PUDL annual table, which is a source-coverage limitation, not physical absence.
5. Treat EIA-860M monthly changelog data as a separate source, not an interchangeable annual snapshot.

## Gate

- Generator identity crosswalk verified: **false**
- Physical commissioning verified: **false**
- Empirical PyPSA dispatch approved: **false**

These observations are suitable for a descriptive data-quality/results appendix, not a commissioning or dispatch claim.

## Official annual source metadata audit (verified 2026-11-18)

Official EIA-860 annual workbook rows independently inspected in successful CI run
[44430217622](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44430217622).
The 2023/2024 source sheet, row, status, nameplate capacity and reported operating dates
were extracted directly from the official workbooks. These are *annual reported fields*,
not evidence of a physical event.

| Plant | Generator | 2023 status / MW | 2024 status / MW | Reported operating month/year | Interpretation |
|---|---|---|---|---|---|
| 50535 | WGNS | RE / 27.0 | OP / 33.6 | 11/1984 both years | **Flag:** 2023 reports retirement 12/2020; 2024 reports OP and different nameplate. Do not assert restart or identity with MWD1. |
| 61446 | PV2 | OP / 45.0 | OP / 45.0 | 05/2023 both years | Stable reported annual attributes |
| 63094 | SBAD1 | OP / 1.1 | OP / 1.1 | 06/2022 both years | Stable reported annual attributes |
| 63094 | SBAD2 | OP / 1.1 | OP / 1.1 | 06/2022 both years | Stable reported annual attributes |
| 65820 | OWS | OP / 50.0 | OP / 50.0 | 09/2023 both years | Stable reported annual attributes |

**Independent validation:** official 2025 EIA-860 metadata gate passed all
29 target keys with zero mismatches for reported operating year, status and
OP-only nameplate capacity in the same CI run. Synthetic negative tests for
year mismatch, capacity mismatch, duplicate official records and missing keys
also passed.

**Open research issue:** obtain plant/operator documentation or EIA-860M
monthly revisions to determine whether WGNS's RE→OP and 27.0→33.6 MW
reflect a correction, reactivation, or another reporting change. None of
these alternatives is established by annual snapshots alone.

**Modeling decision:** maintain separate exact-key historical cohorts;
do not join historical IDs to 2025 target IDs, infer physical commissioning,
or approve empirical PyPSA dispatch until independent crosswalk evidence
is obtained.

## Independent EIA-860M December snapshot contradiction (verified)

Successful CI run [44449378102](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44449378102)
downloaded the official December EIA-860M generator XLSX snapshots and
independently located plant **50535**, generator **WGNS**:

| Source | WGNS worksheet / status evidence | Nameplate | Reported operating date | Reported retirement date |
|---|---|---:|---|---|
| December 2023 EIA-860M | Retired worksheet | 27 MW | 11/1984 | 12/2020 |
| December 2024 EIA-860M | Retired worksheet | 27 MW | 11/1984 | 12/2020 |
| Annual 2023 EIA-860 | Retired and Canceled; RE | 27 MW | 11/1984 | 12/2020 |
| Annual 2024 EIA-860 | Operable; OP | 33.6 MW | 11/1984 | No retirement field extracted |

Monthly source and SHA-256 receipts:
- 2023: `https://www.eia.gov/electricity/data/eia860m/archive/xls/december_generator2023.xlsx`,
  `cb23a95036f99ad6f43c756c5c7d050953337149a452291760240abf881ebf00`
- 2024: `https://www.eia.gov/electricity/data/eia860m/archive/xls/december_generator2024.xlsx`,
  `22c742b72fd7709d4632a92074fa968cc5a728b9c8f0cbc82959b327e0eba8e7`

**Interpretation:** the December 2024 preliminary monthly snapshot and the
2024 annual release disagree on reported status and capacity for the same
plant/generator key. The evidence does not establish a physical restart,
the cause or timing of an administrative correction, or that either snapshot
is necessarily authoritative for the other release's reference date.
The next priority is to inspect the annual release's reporting vintage,
monthly revision history and independent plant/operator documentation.

**Modeling gate remains closed:** do not use WGNS as evidence of new
commissioning, map WGNS to MWD1, or authorize empirical PyPSA dispatch.
