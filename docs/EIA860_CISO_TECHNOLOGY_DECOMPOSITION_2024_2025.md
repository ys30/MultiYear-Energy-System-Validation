# CISO 2024–2025 OP fleet capacity: technology-level decomposition

**Verified source:** [successful GitHub Actions run 41771789078](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41771789078), job 126382928148, commit c92c9160. Official annual EIA-860 CISO plant-BA inventory; exact plant/generator identity match. This is **not** empirical dispatch or physical commissioning evidence.

## Verified technology-level OP nameplate change

| Technology | 2025 minus 2024 (MW) |
| --- | ---: |
| Batteries | +3,862.2 |
| Solar Photovoltaic | +1,849.4 |
| Hydroelectric Pumped Storage | +1,053.0 |
| Conventional Hydroelectric | +215.5 |
| Geothermal | +73.0 |
| Natural Gas Fired Combined Cycle | -157.9 |
| All Other | +8.0 |
| Landfill Gas | -5.5 |
| Natural Gas Fired Combustion Turbine | -1.9 |
| Natural Gas Internal Combustion Engine | +14.9 |
| Onshore Wind Turbine | -8.4 |
| Other Natural Gas | -5.0 |
| Other Waste Biomass | -6.6 |
| Petroleum Liquids | +1.5 |
| Wood/Wood Waste Biomass | +3.6 |
| **Net OP change** | **+6,895.8** |

Batteries plus solar account for 5,711.6 MW, approximately 82.83% of net OP nameplate increase. This is a share of **net change**, not of total generation capacity or electricity supplied.

## Unit-level classifications

- 157 new-to-inventory records, including 63 batteries and 71 solar photovoltaic.
- 16 missing-from-inventory records, including 3 batteries and 2 solar photovoltaic.
- 42 status-changed records, including 3 pumped-storage units and 20 conventional-hydroelectric units.
- 21 nameplate-changed records, including 12 geothermal units.
- 7 technology-changed records; 2,559 unchanged.
- OP net changes by first-match category: +6,339.3 MW new-to-inventory, -379.9 MW missing, +862.4 MW status-changed, +74.0 MW nameplate-changed, 0 MW technology-changed.

**Important:** the +1,053 MW pumped-storage change coincides with status changes for three pumped-storage records. It should not be described as 1,053 MW of newly built pumped-storage capacity without verification of raw status transitions and dates.

## Scientific limitations and next checks

The classifications are mutually exclusive and prioritized (membership, status, technology, nameplate). OP status is not proof of hourly availability. CISO plant BA membership is not a verified operating boundary, and battery power is not energy capacity or firm capacity. Before dispatch: inspect raw change-level JSON for status transitions, operating dates and plant BA changes; validate EIA-930 interchange and independent hourly generation availability. No optimized real-world model result is claimed.

The private CI artifact `ciso-eia860-fleet-transitions` contains the full per-generator changes. Keep manuscript versions outside the repository.
