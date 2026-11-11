# Local verification receipt — Project A PUDL cohort

Date: 2026-11-10 (local session). This receipt is for **EIA-860 source reconciliation**, not a PUDL monthly match.

The archived original GitHub Actions ZIP `github-actions-artifact-13295023796.zip` was opened locally. It contains `fleet_transitions_2024_2025.json`. The 29-row checked-in cohort was compared to all source records selected with `classification == new_to_ciso_inventory` and `current_operating_year_raw < 2025`.

**Executed result: PASS.** Exact Plant ID + Generator ID matches: 29/29; missing keys: 0; status mismatches: 0; reported operating-year mismatches: 0; OP capacity mismatches: 0; total OP MW: 138.1. Floating-point MW comparisons use a tolerance, not bit-exact equality.

This local verification does **not** establish that GitHub Actions cohort tests passed. No verified CI run result is yet available. No actual PUDL changelog has been retrieved or matched, and dispatch remains blocked.
