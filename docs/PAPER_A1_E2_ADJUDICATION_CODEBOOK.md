# Paper A1 — E2 independent generator identity adjudication codebook

**Status:** protocol only; no independent review or identity resolution has been performed. E2 sampling run: [45097563073](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/45097563073), 158 sampled records from eight strata.

## Observation and sampling

Review one *source-year generator key* at a time, keeping the comparison direction and plant-context stratum. Inclusion probabilities are recorded per stratum. Sampling is not a physical-unit census; cases can recur in adjacent comparisons. A reviewer must not assume that a same-plant candidate with similar MW is a physical match.

## Evidence and provenance

For every affirmative or negative physical-lineage judgment, retain exact official EIA archive URL, archive SHA-256, publication vintage, sheet/table, row locator, generator IDs, and relevant status/capacity/date fields. Keep PUDL v2026.11.0 separate from independently retrieved EIA archives. Use EIA-860M monthly records to investigate revision chronology; do not confuse the first *reported* appearance with physical commissioning.

If source evidence is missing, leave official evidence fields blank and classify **unresolved**. A PUDL canonical identifier alone is a comparison baseline, not independent ground truth.

## Allowed adjudicated outcomes

| Label | Meaning | Minimum evidence |
|---|---|---|
| `verified_same_physical_unit` | Distinct record keys describe the same physical generator | Explicit primary-source unit-level continuity or independently verifiable documentary crosswalk |
| `documented_successor` | One unit explicitly replaces/repowers another | Primary-source explicit replacement/repowering relationship and timeline |
| `distinct_units` | Candidate units are demonstrably different | Independent records proving simultaneous distinct operation or explicit distinct-unit evidence |
| `conflicting_evidence` | Credible official sources support incompatible claims | Preserve both source locators, vintages, and contradictions |
| `unresolved` | Insufficient evidence to determine physical relationship | Document searches attempted and missing proof |

No auto-approval based solely on same plant, similar capacity, dates, fuel, or technology. **Never equate a source-only record with construction or retirement.**

## Review workflow

1. Generate frozen E2 queue with deterministic seed and record inclusion probabilities.
2. Collector obtains official annual and, when relevant, monthly archive records and exact locators.
3. Reviewer 1 and reviewer 2 independently record decisions without viewing each other's decisions or automated matching suggestions.
4. A separate adjudicator resolves disagreements with documented evidence; unresolved is an acceptable outcome.
5. Only after adjudication, compare B0 exact key, B1 PUDL published entity resolution (if available and schema-verified), and B2 conservative primary-source gate.
6. Report stratified coverage, abstention, false-link risk and disagreements; calculate performance metrics only on eligible adjudicated cases, with selection weights where appropriate.

## Mandatory output checks

- Preserve original sampled key and source vintage; never overwrite the frozen queue.
- Every asserted physical relationship must carry source locators and evidence type.
- Distinguish reviewed from adjudicated; no blank decision should be treated as negative.
- Report population strata and sample counts (158 actual; target was 160).
- Do not publish E2 accuracy/precision/recall or E4 dispatch impacts before review and model validation.
