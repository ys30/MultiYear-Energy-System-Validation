# Mesa Wind repower: independent documentary evidence (2026-11-19)

## Evidence established

Official EIA-860 annual workbooks identify plant 50535 as **Mesa Wind Power LLC**, utility field **Brookfield Renewable Trading and Marketing LP**, generator **WGNS**. The 2023 annual entry is RE / 27 MW / retired December 2020; 2024 annual is OP / 33.6 MW. All twelve 2024 EIA-860M monthly archived workbooks instead retain WGNS on the Retired sheet at 27 MW. See `WGNS_CROSS_VINTAGE_DISCREPANCY.md` and CI run 44611496067.

Independent documents show an actual **Mesa Wind repowering project**, but do not establish that the *old generator ID WGNS* restarted:

1. **U.S. Bureau of Land Management (BLM), 2020-09-30**, *BLM approves Mesa Wind Repower Project near Palm Springs*. The existing approximately 30 MW project, built in 1983, would remove ~460 old turbines and install up to nine new turbines. Source: https://www.blm.gov/press-release/blm-approves-mesa-wind-repower-project-near-palm-springs
2. **Brookfield Renewable**, *Mesa Re-Power* project page. Project proposal removes ~460 legacy turbines and installs eight new WTGs with approximately 30 MW output. Source: https://mesarepower.brookfieldusprojects.com/
3. **FERC Market-Based Rate asset appendix**, Mesa Wind Power LLC, docket ER13-1346-000. The publicly indexed asset row reports **33.60 MW** with a **30 MW point-of-interconnection limit**. Source: https://mbrweb.ferc.gov/SearchMBRAssetAppendix/AssetAppendixDetails?AssetAppendixId=57951 . The displayed asset appendix is a current/revised view; **do not attribute the 33.60 MW row to the 2024 publication vintage** without a dated snapshot.
4. **BLM Decision Record**, Mesa Wind Repower Project: decommissioning ~400 existing turbines, installing nine new turbines, selected alternative up to 30 MW. Source: https://eplanning.blm.gov/public_projects/1504648/200364317/20027264/250033466/3.%20Mesa%20Draft%20Decision%20Record%20%28508%29.pdf
5. **Independent EIA-derived plant listing (secondary; requires official verification)**: plant 50535 lists **MWD1** 30 MW, June 2024, and **WGNS** retired December 2020. Source: https://energy.statnorth.us/power-plants/ca/mesa-wind-power-llc-50535 . Do not treat this listing as primary proof of a generator-ID crosswalk.

## Verified 2025 official MWD1 record

The EIA-860 **2025 annual generator workbook** contains plant **50535**, generator **MWD1**, in the **Operable** worksheet, row **9577**. Its reported fields are:

- Status **OP**
- Nameplate capacity **30 MW**
- Operating Month **6**, Operating Year **2024** (reported June 2024 operation)
- Nameplate Power Factor **0.95**

This was directly transcribed from the official annual archive by the repository's audit workflow, not inferred from a third-party listing. Provenance: [CI run 44678237561](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44678237561), `official-eia860-archive-inventory` job, `OFFICIAL_2025_TARGET_METADATA` receipt for plant 50535 / MWD1.

**Important:** A 2025 annual workbook reporting a June 2024 operating date does not by itself prove the exact commissioning date or that the same generator ID was present in the **2024 annual publication vintage**. MWD1 (30 MW) and legacy WGNS (27 MW in monthly / 33.6 MW in annual 2024) must not be added as independent contemporaneous capacity without establishing unit identity and reporting scope.

## Interpretation and safeguards

- **Confirmed:** repower project documented by BLM and Brookfield; FERC asset view reports 33.60 MW and a 30 MW interconnection limit.
- **Confirmed:** annual vs monthly EIA source disagreement for *WGNS* persists.
- **Plausible, not proven:** annual 2024 WGNS may reflect plant-level repower information assigned to a legacy generator ID or a data-vintage/reporting mismatch.
- **Not proven:** WGNS physically restarted, WGNS and MWD1 are identical physical units, or a dated EIA correction caused the discrepancy.
- **Critical distinction:** **33.60 MW nameplate/asset capacity is not interchangeable with 30 MW interconnection/export limit.**
- The 2025 target cohort and historical generator-ID crosswalk remain **unverified**; empirical PyPSA dispatch remains **blocked**.

## Follow-up validation

1. Inspect the official 2024 and 2025 EIA-860 generator workbooks for **both WGNS and MWD1**, including status, operating dates, technology, turbine counts and unit nameplate; preserve row provenance and archive SHA-256.
2. Inspect EIA-860M **2025** monthly archives to identify the first month MWD1 appears and whether WGNS remains retired, without treating absence as proof of physical shutdown.
3. Find a dated FERC asset appendix or contemporaneous filing to establish whether the 33.60 MW entry was reported in 2024.
4. Reconcile BLM's selected nine-turbine authorization with Brookfield's eight-turbine project description using dated as-built records; do not assume a contradiction between proposal and final installation.
5. Request an EIA clarification if WGNS annual 2024 OP/33.6 MW cannot be explained from official reporting revisions.

**Manuscript-safe statement:** Government permitting and developer materials document repowering of Mesa Wind; independently, a FERC asset record reports 33.60 MW with a 30 MW interconnection limit. This context is consistent with a facility undergoing substantial changes but does not resolve why 2024 annual EIA-860 marks legacy generator WGNS operable while all twelve archived monthly EIA-860M reports classify it retired.
