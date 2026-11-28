# WGNS annual–monthly discrepancy: causal evidence checklist

**Scope:** EIA plant 50535, generator WGNS. This is an evidence acquisition protocol, not a finding about the reason for the discrepancy.

## Observed facts

- Official EIA-860 annual 2023: retired (RE), 27 MW, retirement December 2020.
- Official EIA-860 annual 2024: operable (OP), 33.6 MW, operating date November 1984.
- Official EIA-860M December 2023 and **every January–December 2024 monthly archive snapshot**: Retired worksheet, 27 MW, operating date November 1984, retirement December 2020.
- Source and integrity receipts: `docs/WGNS_CROSS_VINTAGE_DISCREPANCY.md`; CI [44456551626](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44456551626).

## Official annual generator-row identity fields (verified in CI)

The annual EIA-860 generator workbook reports the following for plant **50535**, generator **WGNS**, in **both** 2023 and 2024:

- **Plant Name:** `Mesa Wind Power LLC`
- **Utility Name:** `Brookfield Renewable Trading and Marketing LP`
- **Technology:** `Onshore Wind Turbine`
- **Energy Source 1:** `WND`
- **Operating Month/Year:** `11/1984`

The utility-name field is **not** independently verified as the physical operator, owner, or entity responsible for reporting. This is an official source-field transcription, not a physical generator identity crosswalk. CI provenance: [run 44611496067](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44611496067), `official-eia860-archive-inventory` job, `OFFICIAL_WGNS_IDENTITY_FIELDS` receipts. The 2023/2024 status and capacity contradiction remains unresolved.

## Competing explanations — not yet established

| Hypothesis | Distinguishing evidence | Interpretation if found |
|---|---|---|
| Annual-file revision / correction | EIA-860 2024 release notes, archived editions and revision timestamps; same key's status/capacity in earlier annual editions | Supports a *data-version change*, not necessarily a physical event |
| Different annual vs monthly reporting / inclusion rules | EIA methodology, reference dates, status definitions, questionnaire and instructions | Supports a *measurement-definition difference* |
| Generator uprate or reconfiguration | Utility/operator reports, regulatory filings, EIA plant-level generator characteristics and dated modification records | May support a *physical capacity change* only with direct evidence |
| Incorrect or reused generator ID | Independent generator serial/technology/operator identifiers, dated generator lists | May support *ID mismatch*, not a valid crosswalk without corroboration |
| Unresolved source error | Official correction notice or EIA data inquiry response | Supports an explicit source-quality exception |

## Required provenance for each new item

Record the exact document title, publisher, source URL, publication/revision date, reference period, download date, relevant table/page/row, raw file SHA-256 if downloaded, and a short verbatim field transcription. Distinguish *publication date* from *reference year*. Never equate missing monthly rows with commissioning or shutdown.

## Decision rules

1. The annual-vs-monthly contradiction is **verified**; its cause is **unknown**.
2. Do not label annual OP as proof of physical restart or 33.6 MW as a proven installed-capacity increase.
3. Do not map WGNS to 2025 target generator MWD1 without independent physical identity evidence.
4. Do not admit these historical target keys into empirical PyPSA dispatch until generator identity, timestamps and relevant physical quantities are validated.
5. If no official revision evidence is found, retain the contradiction as a documented limitation and data-quality case study.

## Next evidence retrieval

1. Obtain EIA-860 annual 2024 release metadata and generator status definitions from official EIA documentation.
2. Check whether an archived prior 2024 annual workbook exists and compare WGNS rows byte-for-byte with the currently downloaded annual release.
3. Using the official **Mesa Wind Power LLC** plant name and **Brookfield Renewable Trading and Marketing LP** utility field, seek independent operator/owner records and dated generator capacity changes. Do not conflate the EIA utility field with ownership or operational control.
4. If necessary, send EIA a focused inquiry quoting the exact two source rows and asking about vintage/revisions; do not assert a correction before a reply.
