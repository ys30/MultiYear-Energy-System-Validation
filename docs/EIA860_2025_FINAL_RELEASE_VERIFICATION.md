# EIA-860 2025 annual final release verification (2026-11-10)

**Verified official EIA publication status:** EIA posted the **final 2025 Form EIA-860 Annual Electric Generator Report on September 10, 2026**. EIA's historical state-data page labels 2025 annual data final and lists the EIA-860 release date 2026-09-10. The annual EIA-860 detailed-data page includes the 2025 ZIP. This is **not** the preliminary monthly EIA-860M dataset.

Official references:
- https://www.eia.gov/electricity/data/state/index.php
- https://www.eia.gov/electricity/data/eia860/
- https://www.eia.gov/about/new/index.php?r=9390%2F1000

**Source archive provenance independently checked in archived CI artifacts:**

| Year | Annual ZIP source | Raw ZIP SHA256 |
|---|---|---|
| 2024 | https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip | `0aaae04812cd4ab87a3e346bdf93848a3cc15053fd4dc2a4cf82d2aeac95f12b` |
| 2025 | https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip | `2b27929d26cc1da9ad6a530da1cac6718cd8496098ee560c4d47cfffd96d08ba` |

The digests were recomputed from the raw ZIP bytes inside private GitHub Actions source artifacts 13281394181 (2024) and 13282152290 (2025), and matched the archived source-inventory manifests. They identify the **specific downloaded archive versions** used in the fleet comparison, not a guarantee that EIA will never revise a published file.

**Research consequence:** remove the earlier uncertainty that the 2025 annual EIA-860 source may be preliminary. This resolves only the *annual release-status* gate. It does **not** resolve plant BA operational boundary, EIA-930 source anomalies, physical commissioning, storage energy constraints, hourly availability, interchange, costs, or empirical dispatch readiness.

**Empirical dispatch approved: false.**
