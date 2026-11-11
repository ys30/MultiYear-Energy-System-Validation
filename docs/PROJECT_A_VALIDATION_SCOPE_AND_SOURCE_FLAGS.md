# Project A: validation scope and source-inventory flags

## Archived source evidence

Archived GitHub Actions artifact **13295023796** contains `2024/source_inventory.json`, `2025/source_inventory.json`, and `fleet_transitions_2024_2025.json`.

Both annual source-inventory JSON files explicitly report:

| Field | 2024 | 2025 |
|---|---|---|
| `generation_fleet_validated` | `false` | `false` |
| `balancing_authority_mapping_validated` | `false` | `false` |
| `dispatch_model_approved` | `false` | `false` |

The 29-record pre-2025 operating-year cohort has separately passed an **internal consistency reconciliation** against the archived fleet-transition JSON: 29 matching plant/generator keys, zero status/year/capacity mismatches, and 138.1 MW of OP nameplate. This checks the *derived cohort against its archived upstream transition output*. It does **not** independently validate the full EIA-860 fleet, original BA assignment, or any physical commissioning event.

## Reporting rules

- Refer to the 29/29 result as **cohort-to-transition-artifact reconciliation**, not complete EIA-860 validation.
- Treat Plant-sheet BA crosswalk findings as source-level descriptive checks, with whole-source BA validation still open.
- Never set `dispatch_model_approved` to true based on cohort reconciliation, a synthetic smoke test, or a PUDL changelog match.
- PUDL EIA-860M changelog matching is not independent physical commissioning evidence; first changelog date is not first operating date.
- Preserve explicit failure/unknown states in the manuscript and all dashboards until independent full-scope checks have passed.

## Outstanding acceptance gates

1. Full annual generator-fleet and BA mapping checks against official original workbooks.
2. Immutable PUDL release file acquisition, checksum verification, and real 29-key changelog match.
3. GitHub Actions test results and archived artifact availability.
4. Separate empirical PyPSA dispatch input gates (generation, interchange, storage, costs, topology, and consistency).
