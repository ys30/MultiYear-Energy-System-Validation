# R02 pilot: public plant identity and chronology screening (2026-11-06)

**Scope:** exploratory external-source screening only. The EIA-860 2025 OP
generator audit remains the canonical source for generator technology and
nameplate. The links below are secondary/public plant profiles and **must not
be promoted to verified equipment parameters** without primary documentation.

| EIA plant ID | Public identity | Evidence | Follow-up |
|---|---|---|---|
| 57695 | Topaz Solar Farm | https://www.interconnection.fyi/eia/plant/57695 | Search owner/First Solar documents for plant-specific module and tracking configuration, with effective year |
| 64210 | Bellefield Solar and Energy Storage Farm | https://askthegrid.com/assets/facilities/bellefield-solar-and-energy-storage-farm | **Critical**: reported solar-plus-battery hybrid; independently verify the 2025-07 commercial operation date and storage interconnection/dispatch treatment before using July weather as an operating-plant validation window |
| 7526 | Solano Wind | https://www.interconnection.fyi/eia/plant/7526 | Generator records span different vintages; verify phase-by-phase turbine model, hub height and repowering |
| 57514 | Ocotillo Express LLC | https://www.inframap.pro/plants/57514/ocotillo-express-llc | Find owner turbine model, hub-height and power-curve evidence |
| 57484 | Manzana Wind LLC | https://theenergyvine.com/generation/california/wind | Find operator/permit turbine specifications |
| 57373 | Identity pending primary-source confirmation | EIA-860 2025 plant workbook | Extract official name and generator IDs; find manufacturer/permit |

## Critical empirical constraints

1. NASA POWER July 2025 weather at a plant coordinate **does not prove** that
   the plant was operating in July 2025. Cross-check EIA generator operating
   month/year and EIA-923 July generation (where available). Do not treat
   post-commissioning weather as measured generation.
2. A hybrid solar-plus-battery plant needs a distinct storage representation;
   500 MW of PV cannot be silently equated to total site export, and battery
   nameplate cannot be counted as solar generation. Check grid export limits.
3. Multi-phase wind plants may have multiple turbine types and vintages.
   Plant-average nameplate does not determine hub height or turbine power curve.
4. These secondary links identify leads, not verified parameter values.
   Preserve all 39 unknown engineering fields until plant-specific primary
   documentation is independently reviewed.
5. No renewable availability series or empirical PyPSA dispatch is approved.
