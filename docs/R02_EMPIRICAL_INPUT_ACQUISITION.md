# R02 empirical dispatch input acquisition checklist

Status: **BLOCKED**. This is a provenance and acceptance checklist, not a claim of ingested empirical inputs.

| Input | Candidate source | Required evidence | Status |
| --- | --- | --- | --- |
| Hourly renewable availability | EIA-930 generation by energy source and/or CAISO OASIS production; weather-driven profiles only with validated mapping | BA and technology scope, UTC hour semantics, 2024–2025 completeness, units, curtailment treatment | Not verified |
| Thermal operating costs | EIA-923 fuel receipts/costs + EIA-860 technology and heat-rate assumptions or validated plant-level cost data | Fuel prices by period, heat-rate basis, emissions and VOM assumptions, coverage | Not verified |
| Storage constraints | EIA-860 storage power/energy capacity, plant data, validated efficiency/SOC assumptions | MW/MWh ratio, duration, round-trip efficiency, initial/final SOC policy | Not verified |
| Interchange boundary | EIA-930 BA interchange and/or CAISO OASIS interchange with explicit sign conventions | Boundary and counterparties, hourly values, balance consistency, import/export treatment | Not verified |

The R02 load-quality gate separately blocks the flagged 2025-07-31 hour until source discrepancy policy is resolved. Do not infer availability factors from demand, use capacity as generation, silently fill missing hours, or call assumed storage efficiencies measured. All candidate inputs require independent provenance and coverage checks.

Implementation: `src/multiyear_energy_validation/r02_input_manifest.py` checks required metadata and separates self-attested evidence from final dispatch approval. A numerical model validation and load gate are still mandatory.
