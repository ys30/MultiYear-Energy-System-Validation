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
