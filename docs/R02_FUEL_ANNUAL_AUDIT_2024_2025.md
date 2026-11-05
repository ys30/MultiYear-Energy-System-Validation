# R02 EIA CISO fuel-type annual audit — 2024–2025

Verified CI: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41963714687

| Metric | 2024 | 2025 |
| --- | ---: | ---: |
| Hourly periods | 8,760 | 8,760 |
| Expected UTC periods | 8,784 | 8,760 |
| Records | 70,067 | 70,455 |
| Invalid records | 0 | 0 |
| Coverage pass | No | Yes |

2024 missing UTC hour labels form a continuous 24-hour block from `2024-11-02T08` through `2024-11-03T07`, inclusive. This is temporally near daylight-saving transition but causality is **not established**. Do not fill this gap with zero or interpolation without an explicitly separated sensitivity analysis.

2025 `GEO` appears for 375 hours, from `2025-12-16T09` through `2025-12-31T23`. The absence of this category before its first report is **not evidence of zero geothermal generation**. The taxonomy requires provider-definition and reclassification checks before comparing annual fuel shares. Some 2024 COL/NUC/OIL rows are absent; do not automatically equate omitted rows with zero.

The 2025 hourly coverage check passes but the separate 2025-07-31 EIA fuel-versus-region NG inconsistency remains unresolved. These fuel-type series are **observed generation**, not renewable availability. The code in `fuel_eligibility.py` blocks unqualified full-year fuel-mix comparisons when gaps or taxonomy changes exist. R02 dispatch stays blocked.
