# R02a cross-endpoint acceptance record

**Scope:** CISO, EIA-930 raw hour-ending periods `2025-07-31T19` through `T23`, comparing the region-data `NG` series to the signed sum of fuel-type-data rows. This is a source consistency check, **not** a physical energy balance or corrected load estimate.

## Evidence currently established

Historical audit recorded region NG = 27,732 MWh and fuel sum = 30,003 MWh at `T21`, giving +2,271 MWh. Neighboring hours had differences 0, -1, 0 and +1 MWh. The +2,271 MWh difference numerically matches a nuclear fuel value, but the cause is **not established**. Independent CAISO demand did not corroborate the EIA regional demand trough.

## Implemented checks (not yet certified as passing)

- `eia_cross_endpoint_audit.py`: signed fuel sums, duplicate detection, no missing-hour zero fill, consistent fuel categories.
- `eia_cross_endpoint_cli.py`: offline JSON inputs, provenance URL screening, UTC timestamp, SHA256.
- `eia_cross_endpoint_live.py`: bounded EIA endpoint downloads and five-hour audit; keeps EIA key out of provenance URLs and sanitized HTTP/network errors.
- `r02a-cross-endpoint-tests.yml`: offline regression tests.
- `r02a-live-cross-endpoint.yml`: offline tests first, then live API download, with private 14-day artifacts.

The regression fixture uses *synthetic fuel rows* that reproduce historical aggregate differences. Its successful execution, even if confirmed, would not establish the source-level reason for the discrepancy.

## Required acceptance evidence

1. Record the live GitHub Actions run URL, job conclusion, UTC retrieval time, and artifact identifier.
2. Download `region_raw.json`, `fuel_raw.json`, and `cross_endpoint_audit.json`; verify SHA256 of both archived raw responses against the report.
3. Verify every raw row's respondent, EIA period label, units, fuel code, and signed value; investigate negative `OTH` and any omitted/renamed fuel category.
4. Confirm whether the fresh `T21` discrepancy is still +2,271 MWh, and compare all five periods against the archived historical audit. A changed value is a source revision to investigate, not an automatic code failure.
5. Check official EIA endpoint definitions and revision semantics before assigning an explanation (including the nuclear coincidence).
6. Add a dated evidence-register entry with links to the run/artifact and a disposition: `reconciled`, `unresolved`, or `source-revised`.

## Fail-closed research decision

Until steps 1–6 are independently verified, `empirical_dispatch_approved = false`. No raw demand correction, generation availability inference, or manuscript claim of causal reconciliation is authorized by these diagnostics.

**Retention warning:** GitHub artifacts are configured for 14 days. Download the evidence to approved durable private storage before expiration. Do not place API keys or raw source query strings containing secrets in committed files.
