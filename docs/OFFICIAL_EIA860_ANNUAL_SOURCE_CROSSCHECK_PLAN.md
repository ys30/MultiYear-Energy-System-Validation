# Project A — Independent official EIA-860 annual cross-check

## Authoritative source

US Energy Information Administration (EIA), Form EIA-860 detailed annual generator data:
https://www.eia.gov/electricity/data/eia860/

Official annual ZIP endpoints to independently retrieve and checksum:
- 2023: https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602023.zip
- 2024: https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip
- 2025: https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip

These are **source URLs**, not a claim that the files have been downloaded or independently inspected. Before processing, verify HTTP status, ZIP integrity, archive member names, raw ZIP SHA256, spreadsheet sheet names and header row positions for each year. Preserve immutable raw downloads outside Git and record checksums in the evidence receipt.

EIA documents generator files `3_1_GeneratorYyyyy` with **Operable**, **Proposed**, and **Retired and Canceled** tabs. Operable includes operating, out-of-service, and standby generators. Do not restrict matching to OP alone. Retired and Canceled is not a complete historical retirement register. EIA-860M is preliminary monthly inventory and must not substitute for annual source.

## Exact identity audit

Match **plant ID + normalized generator ID + reporting year**, retaining the original ID string and normalization rules. Inspect all three tabs, but report tab provenance and status explicitly. No fuzzy joining and no assumption that similar IDs are aliases.

| Plant | Historical PUDL IDs in both 2023/24 | 2025 target cohort IDs |
|---|---|---|
| 50535 | WGNS | MWD1 |
| 61446 | PV2 | BA2 |
| 63094 | SBAD1; SBAD2 | G100; G200; SOLAR |
| 65820 | OWS | OWB |

Review all 29 target keys, including the 23 at plants without 2023/24 PUDL annual records, to distinguish a PUDL coverage limitation from official EIA annual reporting coverage.

## Required output columns

`source_year,source_zip_sha256,source_member,sheet,plant_id_eia,generator_id_original,generator_id_normalized,matched_target_key,reported_status,reported_operating_year,nameplate_mw,source_row_number`.

Include an explicit `unmatched` row for every target/year with no official record and keep its interpretation `official_annual_record_unmatched`, **not** `physically_absent`.

## Verification gates

- Three official annual ZIPs fetched and raw SHA256 pinned: **pending**
- Official workbook headers and tabs verified: **pending**
- 87 target-year exact-key comparison: **pending**
- Historical generator alias/renaming independently documented: **pending**
- Physical commissioning verified: **false**
- Empirical PyPSA dispatch approved: **false**

PUDL descriptive evidence is already reproducible in GitHub Actions run
https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44242038951 .
This independent official EIA check must not reuse the PUDL annual table as a stand-in for original survey spreadsheets.


## Verified official workbook exact-key audit (2026-11-18)

GitHub Actions run 44387479905 executed `scripts/audit_official_eia860_generator_keys.py` against independently downloaded official EIA-860 annual Generator workbooks. The parsing and matching steps succeeded; the workflow's overall failure was caused by exhausted GitHub Actions artifact storage, not a failed data assertion. Follow-up run 44390939797 succeeded with quota-blocked artifact uploads disabled.

| Year | Official annual exact generator keys | PUDL v2026.11.0 annual exact generator keys |
|---|---:|---:|
| 2023 | 0 / 29 | 0 / 29 |
| 2024 | 0 / 29 | 0 / 29 |
| 2025 | 29 / 29 | 29 / 29 |

Official ZIP SHA256 (independent download receipts):
- 2023: `1447e23e608bea1523961542a90eb93ea86715067a37f211282541461049b46f`
- 2024: `0aaae04812cd4ab87a3e346bdf93848a3cc15053fd4dc2a4cf82d2aeac95f12b`
- 2025: `2b27929d26cc1da9ad6a530da1cac6718cd8496098ee560c4d47cfffd96d08ba`

This is **agreement on the target-key presence/absence counts**, not a validated historical generator crosswalk, physical commissioning chronology, row-level metadata equivalence, or evidence of physical absence. In particular, the official workbooks have multiple operational/status sheets; a key found on any recognized sheet is counted as an exact key match. A subsequent audit must compare sheet/status, capacity, and operating-year metadata without silently merging distinct records.

The 87-row audit JSON is generated within CI, but artifact upload is temporarily disabled due to the account's GitHub Actions artifact storage quota. No empirical dispatch approval is implied.
