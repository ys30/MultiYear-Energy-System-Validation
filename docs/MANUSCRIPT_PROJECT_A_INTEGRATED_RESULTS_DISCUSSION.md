# Project A manuscript integration: observed demand and annual fleet transitions

**Status:** evidence-based Results/Discussion integration draft, audited 2026-11-10. The 2025 EIA-860 annual final release and both archive digests are documented separately. This document uses previously successful source-intake/transition CI artifacts plus an independently repeated reading of the original 2024/2025 EIA-860 Plant worksheets. **No new PyPSA empirical optimization.**

## Scientific framing

**Question:** How much of the apparent 2024–2025 CISO generator-fleet change represents changes in annual reported operable inventory, and which mechanisms prevent direct interpretation as newly commissioned or dispatchable capacity?

**Contribution:** a reproducible, identity-matched accounting bridge that separates generator-record membership, status transitions and nameplate revisions, with original Plant-sheet checks of BA assignment for the historical-operating-year entrant subgroup. Observed EIA-930 load is independently staged; it is not equated with verified hourly supply.

## Results: demand coverage and fleet structure

The normalized CISO hourly demand series contains 8,784 records for leap-year 2024 and 8,760 for 2025, with recorded annual totals of 224,030,258 and 224,023,764 MWh. These are EIA-930 reported series, not an independent proof that all source observations are anomaly-free.

Identity-matched annual EIA-860 CISO OP inventory contains 2,645 generator records in 2024 and 2,786 in 2025. Reported OP nameplate increased from 85,634.2 to 92,530.0 MW, or 6,895.8 MW (+8.05%). The first-match, mutually exclusive change bridge assigns +6,339.3 MW to new-to-CISO-inventory records, −379.9 MW to missing records, +862.4 MW to status changes, and +74.0 MW to nameplate changes. Batteries (+3,862.2 MW) and solar photovoltaic (+1,849.4 MW) account for 82.83% of the **net inventory OP nameplate change**, not generation, availability or firm capacity.

Of 157 newly present generator records, **128** report operating year 2025 (6,201.2 MW OP); **29** report a year before 2025 (138.1 MW OP). Of those 29 historical-year records, 23 are OP, one OS and five SB. Original Plant worksheets reveal **four** plant IDs assigned CISO in both years (six entrant generator records; 103.6 MW OP) and **16** plant IDs absent from the 2024 Plant worksheet (23 entrant records; 34.5 MW OP). Neither subgroup alone proves commissioning or the cause of first appearance. The 6,201.2 MW in the reported-2025 cohort is numerically **89.93% of the net 6,895.8 MW increase**, but these are different accounting denominators and this ratio is **not a commissioning fraction**.

At Helms Pumped Storage (Plant 6100), three 351-MW generator records report June 1984 operating dates in both years and status OA→OP. The Plant worksheet reports BA=CISO in both years. Thus the +1,053.0 MW OP inventory contribution is a **status transition within a consistently CISO-assigned plant**, not evidence of 2025 construction or BA reassignment.

## Results: independent source consistency diagnostic

A same-run EIA-930 raw cross-endpoint audit of CISO 2025-07-31 T19–T23 retrieved five regional net-generation values and 40 signed fuel-category values. Fuel-category sum minus regional NG equals [0, −1, +2,271, 0, +1] MWh, with the localized discrepancy at T21. The coincidence between +2,271 MWh and the T21 nuclear category does **not** identify its cause. A separate CISO demand trough at T21 is an additional observation, not a validated source correction. This five-hour case is a **targeted anomaly**, not a prevalence estimate across 2025.

## Discussion: interpretation and model boundary

Three distinct mechanisms appear in the annual comparison: (i) newly present generator IDs at already-CISO plants, (ii) plants absent from the earlier annual Plant worksheet, and (iii) changes of status for historically operating assets. All can change an annual inventory without proving physical construction or hourly available capacity. Consequently the annual nameplate bridge can support a structural inventory comparison but cannot yet support resource adequacy, realized renewable generation, cost, emissions or empirical dispatch conclusions. A synthetic 24-hour PyPSA/HiGHS smoke test validates only the solver path.

The main methodological implication is to treat source provenance, temporal precision, reporting scope, storage energy ratings, interchange and hourly availability as **separate acceptance gates** rather than inferring them from a successful annual inventory join. This is particularly important for storage, where MW power ratings do not determine MWh energy capacity or operating duration.

## Tables and figure register (freeze scope)

- **Table 1:** 2024/2025 EIA-930 hourly coverage, annual demand and source caveats.
- **Table 2:** OP capacity bridge by mutually exclusive generator-record class.
- **Figure 1:** technology-level net OP capacity change, with negative values retained and the denominator explicitly identified.
- **Figure 2:** 2025 entrant records by reported operating-year cohort, distinguishing counts from OP MW. The Plant-sheet membership crosswalk is a separate text/table diagnostic and **must not** be claimed to appear in this figure unless actually plotted.
- **Figure 3 (optional/supplement):** localized R02a five-hour signed generation discrepancy with clear targeted-case caption.

Do **not** add an empirical dispatch figure until its input gate passes. The **2025 final annual EIA-860 release has been verified**; this resolves publication status only, not operational input admissibility. See [final release and source SHA256 verification](EIA860_2025_FINAL_RELEASE_VERIFICATION.md).

## Evidence links

- [Load-only baseline](PYPSA_LOAD_ONLY_BASELINE.md)
- [Technology decomposition](EIA860_CISO_TECHNOLOGY_DECOMPOSITION_2024_2025.md)
- [Operating-year cohorts](EIA860_CISO_OPERATING_YEAR_COHORTS_2024_2025.md)
- [Status transitions](EIA860_CISO_STATUS_TRANSITIONS_2024_2025.md)
- [Plant BA crosswalk](EIA860_PRE2025_ENTRANTS_PLANT_BA_CROSSWALK.md)
- [R02a same-run evidence](R02A_SAME_RUN_RAW_EVIDENCE_2026-11-10.md)
- [2025 EIA-860 final release and source archive SHA256](EIA860_2025_FINAL_RELEASE_VERIFICATION.md)

**Approval status:** annual inventory accounting verified; physical commissioning and operational boundary unresolved; empirical_dispatch_approved=false.
