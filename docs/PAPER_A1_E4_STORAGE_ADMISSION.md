# E4 storage rating evidence and admission
Source: successful run 45759622217; pinned EIA860 2023–2025 archives and PUDL annual generators. Exact annual plant/generator keys, OP only. This is upstream consistency, not independent physical lineage.

| Year | Battery records | Valid ratings | PUDL MW | Valid MW | Valid MWh |
|---|---:|---:|---:|---:|---:|
|2023|573|572|16023.9|15973.9|43775.1|
|2024|759|757|27191|27187|74077.9|
|2025|980|978|42984.6|42980.6|119337.7|

Valid requires positive MW, MWh, charge and discharge ratings and MW agreement within 0.01 MW. Missing ratings are not zero. National pumped hydro OP records 143,144,145 and MW 20869.3,20987.1,21931.2; zero matches to this storage workbook, so energy capacity is unavailable from this source, not zero.

2025 selected BA battery MW/MWh: AZPS 2352.8/8777.4; CISO 15519.3/53186.7; ERCO 13709.3/21253.8; IPCO 459/1832; PNM 908.2/3739; PSCO 364/1104.6. PACW no OP battery row in this cohort. All selected 2024–25 battery records have valid ratings. 2023 AZPS 50 MW lacks valid ratings.

Admission: retain per-generator ratings and separate charge/discharge limits. S0 uses earlier snapshot; S1 requires separate signed unmatched energy and charge/discharge accounting with nonnegative aggregate checks, not later-year duration multiplied by counterfactual MW. S2 uses later snapshot. Unknown ratings remain explicitly unresolved; sensitivity assumptions separately labeled. Pumped hydro requires alternative evidence or explicit duration sensitivity. Annual snapshots are not hourly commissioning histories. No historical dispatch or adequacy claim is admitted by this audit.
