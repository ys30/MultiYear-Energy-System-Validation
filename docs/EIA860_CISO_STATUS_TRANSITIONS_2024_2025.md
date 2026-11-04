# Verified 2024–2025 CISO generator status transitions

**Evidence:** [successful CI run 41772065717](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41772065717), job 126383817592, commit b356e878. This report is an annual EIA-860 inventory status audit, **not** a dispatch, commissioning or reliability result.

## Key verified transitions

| Technology | Previous → current status | Units | OP nameplate delta (MW) |
| --- | --- | ---: | ---: |
| Hydroelectric Pumped Storage | OA → OP | 3 | +1,053.0 |
| Conventional Hydroelectric | OA → OP | 5 | +254.1 |
| Conventional Hydroelectric | OP → OA | 6 | -53.4 |
| Conventional Hydroelectric | OP → SB | 5 | -6.0 |
| Batteries | OP → OA | 3 | -223.5 |
| Batteries | OS → OP | 1 | +1.0 |
| Natural Gas Fired Combined Cycle | OP → OA | 1 | -170.9 |
| Natural Gas Fired Combined Cycle | OA → OP | 2 | +13.0 |
| Solar Photovoltaic | OP → OA | 1 | -6.4 |
| Solar Photovoltaic | OP → OS | 1 | -1.0 |

All 42 status-changing records are included in the CI artifact and the complete transition matrix; the table highlights material changes rather than exhaustively listing every transition.

**Key correction:** The entire +1,053 MW pumped-storage OP delta comes from three units recorded as OA in 2024 and OP in 2025. It must **not** be called new pumped-storage construction. The OP delta from all status-changing units is +862.4 MW after positive and negative transitions.

## Interpretation and research gates

EIA-860 status codes should be defined against the official year-specific data dictionary before labeling OA as available, out of service, or any other plain-language state. A status change can reflect reporting, commissioning, classification or operations; this audit alone does not determine the cause. The annual CISO plant BA code can also change across years.

Next required audits: compare recorded operating month/year for the three pumped-storage units; inspect BA membership for new/missing units; reconcile battery MW against duration and storage MWh; independently source hourly availability, dispatch and interchange. Empirical PyPSA dispatch readiness remains false.
