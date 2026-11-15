# Project A — Official EIA-860 acceptance runbook

## What this run can and cannot establish

A successful `official-eia860-archive-integrity` job independently reproduces
the **CISO-filtered 2024–2025 original-workbook OP inventory and generator-identity
capacity bridge** against pinned official ZIPs. It does not certify CISO
historical BA assignment, PUDL matching, 2025 commissioning, EIA-930 hourly
data, or empirical PyPSA dispatch. The 29 archived historical-entrant operating years were independently checked against the original 2025 Generator workbook: 29/29 matched, zero missing, in run 43670234399. This is a reported-year check, not historical BA membership or actual commissioning certification.

## Run and retrieve evidence

1. Open [the workflow](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/workflows/pudl-cohort-safeguards.yml).
2. Select **Run workflow** on the intended branch, or inspect the run automatically
   triggered by a push. Record the run URL, run ID, attempt, and commit SHA.
3. Inspect the three jobs separately: `cohort-tests`,
   `archived-source-reconciliation`, and
   `official-eia860-archive-integrity`. Do not treat a successful first job
   as evidence that the official-data job passed.
4. Download `project-a-official-eia860-ciso-staging-extracts`,
   `project-a-official-eia860-workbook-schema`, and
   `project-a-official-eia860-integrity-manifest` from the same run.
5. Verify `official-data-acceptance-receipt.json` is present and that its
   `github_commit_sha`, `github_run_id`, and archive SHA-256 values match
   the run. Recompute SHA-256 for every file in `output_file_sha256`.
6. Examine `independent-transition-bridge-rows.csv` and
   `independent-29-entrant-evidence-rows.csv` directly. The latter now includes official original-workbook operating year and a per-record match indicator.
7. Only then revise manuscript evidence language and pin the archived receipt.

## Failure triage

| Failing step | First evidence to inspect | Correct response |
|---|---|---|
| Download ZIP | HTTP status, redirects, size | Check EIA URL and availability; do not replace the pinned source silently |
| SHA-256 / unzip | Expected vs observed digest, ZIP CRC | Preserve both values and investigate source-version change |
| Workbook schema | `official-eia860-workbook-schema.json` | Compare actual sheet names and normalized headers before changing aliases |
| Extract CISO rows | Workbook sheet, row, BA and generator identifiers | Repair schema mapping with a regression fixture; never skip malformed CISO rows |
| OP reconciliation | `independent-op-reconciliation.json` | Check status and nameplate definitions and rounding |
| Capacity bridge | `independent-transition-bridge.json` and row CSV | Check identity, classification, and each component separately |
| Helms audit | `independent-helms-transition.json` | Verify actual OA/OP codes and 351 MW values before changing expected constants |
| 29-entrant audit | `independent-29-entrant-evidence-rows.csv` if produced | Check whether differences reflect reporting or CISO membership; never force a match |
| Receipt | Step logs and partial staging artifacts | Do not call the run accepted; preserve diagnostics |

## Evidence acceptance checklist

- [ ] Correct GitHub run ID, commit, and attempt recorded
- [ ] Both official ZIPs match pinned SHA-256
- [ ] Original workbook schema diagnostic retained
- [ ] 2024 and 2025 CISO generator extracts retained
- [ ] Independent OP totals and four-way bridge pass
- [ ] Helms three-unit cross-check passes
- [ ] All 29 archived entrant keys/statuses/OP capacities cross-check
- [ ] All output SHA-256 values verified
- [ ] Historical operating-year check confirmed 29/29 from run 43670234399; PUDL validation explicitly remains pending
- [ ] Manuscript updated with the *actual* run evidence, not workflow configuration

**Never turn an unchecked box into a success claim.**
