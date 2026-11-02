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
