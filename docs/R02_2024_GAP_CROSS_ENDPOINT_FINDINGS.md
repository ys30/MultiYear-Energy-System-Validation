# R02 — EIA CISO 2024-11-02/03 cross-endpoint gap

Evidence: [successful cross-endpoint CI run](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41967745133).

The 24 consecutive EIA UTC hour labels from `2024-11-02T08` to `2024-11-03T07` contain **24/24 demand (D)** observations, **0/24 region net generation (NG)**, **0/24 total interchange (TI)** and **0/24 fuel-type generation** observations. In the four preceding hours, D and NG and fuel generation are present but TI is missing (0/4); all four endpoint types return data in the four subsequent hours.

Interpretation: this is a *source-specific availability gap*, not a full regional demand gap. No conclusion is justified about why the provider data are missing, whether due to reporting, revision, scheduling or daylight-saving handling.

Policy: keep demand-only observations for descriptive demand statistics, retain missing NG/TI/fuel as missing, and disallow these hours from complete empirical dispatch-input acceptance. Do not infer missing generation or interchange from D. The `endpoint_eligibility.py` module and tests codify this distinction.

Further work: verify EIA revision/provider provenance; seek independent CAISO OASIS or archival supply and interchange records, with explicit time basis and scope, before any recovery sensitivity. 2025 fuel-type `GEO` reporting begins 2025-12-16T09 and remains a separate taxonomy investigation.
