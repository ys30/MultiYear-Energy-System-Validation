# EIA-930 intake — verification checklist

**Status:** CSV adapter and synthetic test fixtures only. No observed EIA-930 dataset has been downloaded, audited or used for scientific conclusions.

## Source candidates

- EIA hourly electric grid monitor / EIA-930: https://www.eia.gov/electricity/gridmonitor/
- EIA API documentation: https://www.eia.gov/opendata/documentation.php

Verify the current provider schema, available time series, definitions, terms, balancing authority coverage and any revisions **before** using the adapter. In particular, distinguish observed demand, demand forecast, net generation and interchange. EIA field labels can vary by export format.

## Import contract

The adapter accepts a user-supplied CSV with a timestamp column containing explicit UTC offsets, an observed-demand column in MW, and optionally a balancing-authority column. Each region-year must contain one observation per UTC hour (8760 or 8784), with no missing or duplicate timestamps.

Example for a verified normalized CSV:

```python
from multiyear_energy_validation.eia930 import audit_csv
report = audit_csv("data/raw/verified_demand.csv", year=2021,
    timestamp_column="time_utc", demand_column="demand_mw",
    region_column="balancing_authority", region="CISO")
print(report)
```

This sample does not establish that any actual source file uses these names or that CISO coverage is complete. Preserve raw source data under ignored `data/raw/` and record source URI, date, checksum, time semantics and transformations separately.

## Next evidence gate

1. Confirm official EIA source endpoint and field meanings.
2. Retrieve real records with a documented access timestamp and checksum.
3. Produce region-year missingness, duplicate and annual-energy audit tables.
4. Only then designate calibration and held-out years.


## Reproducible candidate coverage reports

After verifying a downloaded CSV's column semantics and UTC interval-start convention, create a provenance-linked quality report:

```python
from multiyear_energy_validation.reporting import write_coverage_report

report = write_coverage_report(
    "data/raw/verified_demand.csv", "outputs/coverage",
    year=2021, timestamp_column="time_utc", demand_column="demand_mw",
    region_column="balancing_authority", region="CISO",
    source_uri="REPLACE_WITH_VERIFIED_PROVIDER_URL",
    retrieved_at="REPLACE_WITH_ACTUAL_RETRIEVAL_TIMESTAMP",
)
print(report)
```

This writes `CISO_2021_audit.json` (source SHA256 and all quality checks) and `CISO_2021_table1.csv` (a one-row input for manuscript Table 1). These files are **candidate quality reports**, not evidence of real EIA-930 coverage until actual observed records, variable definitions, provider URL and acquisition timestamp are verified. The function does not download, impute, or redistribute third-party records. A `complete` result only establishes compliance with the declared CSV contract; it does not independently verify the provider or physical meaning of the demand column.


## Command-line audit (no data download)

Once the source schema and timestamp semantics have been independently checked, run:

```bash
python -m multiyear_energy_validation.cli \
  --csv data/raw/verified_demand.csv \
  --output-dir outputs/coverage \
  --year 2021 \
  --timestamp-column time_utc \
  --demand-column demand_mw \
  --region-column balancing_authority \
  --region CISO \
  --source-uri "REPLACE_WITH_OFFICIAL_SOURCE_URL" \
  --retrieved-at "REPLACE_WITH_ACTUAL_UTC_RETRIEVAL_TIME" \
  --confirm-utc-interval-start \
  --confirm-observed-demand-mw
```

The confirmation flags are **user assertions**, not automated verification of the EIA schema. The command returns exit code 0 for complete CSV-contract coverage, 2 for incomplete coverage, and a nonzero error for invalid arguments or unexpected input failures. Do not include the raw CSV in a public commit. Replace placeholders with actual provenance; a successful audit is not by itself empirical validation.
