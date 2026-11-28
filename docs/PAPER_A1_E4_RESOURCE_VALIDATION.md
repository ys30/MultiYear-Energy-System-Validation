# E4 resource validation evidence freeze
## Scope
2024 and 2025, seven BAs, first seven UTC days of January, April, July and October. Year-specific later-vintage spatial weights held constant within each capacity comparison. These are exploratory resource proxies, not admitted availability.
## Reproducible evidence
- Spatial weights: run 45856946706.
- July raw weather: 45859204968; CF: 45860429826; observed comparison: 45860953656.
- July wind sensitivity: 45864227705; scoring: 45865162117.
- Independent seasonal weather: 45866330446; scoring: 45868283257.
- 826560 raw grid-hours, 3306240 raw variable values, 18816 baseline CF rows, 840 wind parameter-window-BA combinations, 141120 sensitivity CF rows.
## Wind results
July baseline mean absolute relative bias 0.54324; July-selected rated 12 m/s and speed multiplier 1.30: 0.36707.
Independent windows, equal BA weights, baseline and July-selected candidate:
| Year | Month | Baseline | Candidate |
|---|---|---|---|
|2024|1|0.40466054|0.34643941|
|2024|4|0.42835217|0.42535377|
|2024|10|0.55672098|0.43224563|
|2025|1|0.47522247|0.39309656|
|2025|4|0.45356998|0.45086902|
|2025|10|0.49540152|0.44429190|
Independent means 0.46898794 and 0.41538272. Independent retrospective minimum 12 m/s x 1.15 (0.40421159), closely followed by 10 m/s x 1.00 (0.40542146). These retrospective rankings are not new held-out evidence. Candidate worst BA absolute bias in October 2025 is 1.16595022 versus baseline 0.81446940.
## Admission
No curve admitted. Observed net generation differs from potential availability, reference capacity coverage may differ from EIA930, generic curve and wind multipliers are not turbine-specific or verified bias corrections. Radiation accumulation semantics remain unverified. Do not tune time shifts by BA correlation. No annual dispatch result. Proposed 126-run factorial is not frozen.
