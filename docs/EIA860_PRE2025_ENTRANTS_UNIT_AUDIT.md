# CISO 2025 inventory entrants with pre-2025 operating year: unit-level audit

**Source:** downloaded and inspected actual `fleet_transitions_2024_2025.json` from GitHub Actions run [41772668659](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41772668659), artifact 13295023796. These are reported EIA-860 annual CISO inventory records; the artifact's change objects do **not** contain previous/current plant BA codes, so this document cannot establish BA reassignment.

## Verified population

- 157 records classified `new_to_ciso_inventory`; 128 report 2025 operating year and **29 report an earlier operating year**.
- The 29 earlier-year records span **20 distinct plant IDs**.
- 23 have current status OP and contribute **138.1 MW OP nameplate**; one has OS (22.5 MW nameplate), and five have SB (17.5 MW nameplate). OS/SB are **not** included in OP MW.
- The five SB records belong to plant 69363, generator IDs G-1 through G-5, each 3.5 MW and reporting operating year 2024.
- The OS record is plant 58472, generator 1, 22.5 MW, reporting operating year 2012.
- Largest OP earlier-year entrants: plant 65820/OWB (battery, 50 MW, 2023), plant 50535/MWD1 (onshore wind, 30 MW, 2024), plant 61446/BA2 (battery, 20 MW, 2023). These three account for **100.0/138.1 MW = 72.41%** of earlier-year entrant OP capacity.

## Separate status-transition control

Three pumped-storage units at plant **6100**, generators **1, 2, 3**, each 351 MW, transitioned **OA→OP**. All report original operating month/year **June 1984 in both annual records**. Their +1,053 MW OP change is a status transition, not evidence of new construction in 2025.

## What can and cannot be inferred

The source artifact supports plant/generator identity, year-specific status, technology, reported operating year/month, and nameplate. It **does not expose BA reassignment histories**. A record newly entering the CISO subset may reflect BA reassignment, reporting scope, late inventory entry, or another process; none is established here. Do not infer commissioning from the first year observed in a BA-filtered inventory. Do not sum OS/SB nameplate into OP growth.

## Required next evidence

1. Retrieve original 2024 and 2025 EIA-860 plant sheets for the 20 plant IDs and compare BA codes, reporting identifiers and source year.
2. Inspect full-generator source rows for plants 65820, 50535 and 61446, which dominate OP MW in the earlier-year cohort.
3. Cross-check 6100 status definitions and plant BA mapping using year-specific source dictionaries.
4. Preserve exact raw archive and versioned analysis output with hashes. Keep dispatch gated until availability, storage MWh, interchange, cost and boundaries are validated.

**Research decision:** historical-year entrant accounting verified; BA reassignment and physical commissioning **unresolved**; empirical PyPSA dispatch **BLOCKED**.
