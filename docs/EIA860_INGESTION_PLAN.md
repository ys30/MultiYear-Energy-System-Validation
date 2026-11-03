# EIA-860 generator fleet ingestion: evidence and boundary plan

## Scope
Target: CISO balancing-authority demand (EIA-930) for 2024 and 2025.
Do **not** substitute California state-wide generating capacity for the
CISO balancing-authority fleet. EIA-860 plant location, balancing-authority
assignment, and EIA-930 operating area must be reconciled before model use.

## Primary source
U.S. Energy Information Administration, Form EIA-860:
https://www.eia.gov/electricity/data/eia860/
Annual generator and plant files provide generator identifiers, nameplate
capacity, operating status and dates, and plant-level characteristics.
The exact source year, worksheet, column labels, download URL, retrieval
date and transformation version must be stored in the ingestion manifest.

## Required raw-to-contract mappings (verify per release)
- `plant_id`: plant identifier, preserving leading zeros if any.
- `generator_id`: generator identifier; key jointly with plant.
- `technology`: generator prime mover + energy source / technology code,
  with a separately versioned mapping table; do not infer from plant name.
- `capacity_mw`: documented nameplate MW field, never net generation MWh.
- `balancing_authority`: verified plant-to-BA assignment for the relevant
  year, cross-checked against boundary definitions.
- `online_date` and `retirement_date`: verified operational dates.
  Year/month-only EIA dates are insufficient for exact hourly commissioning;
  a date imputation policy must be approved and flagged, not silently applied.
- `source_name`, `source_url`, `source_as_of`: complete provenance.

## Explicit blockers
1. EIA-860 is an annual inventory; annual snapshots do not establish hourly
   outages, fuel availability or renewable capacity factors.
2. Nameplate capacity is not dependable capacity or dispatch.
3. The current validator requires ISO calendar dates and rejects missing
   online dates. Source precision must be audited before any transformation.
4. Mid-year commissioning is approximated at UTC midnight in the existing
   status-mask function. It is **not** a physically observed operating hour.
5. Imports, exports, embedded generation and demand accounting require
   reconciliation against EIA-930 before supply adequacy analysis.
6. For 2025, confirm whether a final annual EIA-860 release is available;
   do not silently replace it with preliminary EIA-860M.

## Acceptance checklist
- [ ] Archive original annual ZIP/XLSX/CSV with SHA-256 and URL
- [ ] Verify source-specific columns and status codes
- [ ] Audit BA mapping and duplicate plant-generator IDs
- [ ] Record missing / imprecise operational dates without silent fill
- [ ] Produce source-to-contract crosswalk and rejection report
- [ ] Compare year-specific capacities and flag large differences
- [ ] Independently source hourly availability and interchange
- [ ] Only then approve empirical dispatch input

**Current status:** source ingestion and empirical fleet validation not yet
performed. All prior optimizer smoke results are explicitly synthetic.
