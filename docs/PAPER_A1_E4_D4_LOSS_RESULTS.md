# D4 uniform PV output derate development results

Run 45954302470 succeeded in both years, using paired same-fleet artifacts from run 45951342303. Seven fixed output multipliers, 98 BA-year-scenario metrics. NRMSE = RMSE / mean observed MW, equal BA weights.

| Derate | Mean NRMSE 2024 | Mean NRMSE 2025 | Worst NRMSE 2024 | Worst NRMSE 2025 | Wins vs PV0 2024 | Wins vs PV0 2025 |
|---|---:|---:|---:|---:|---:|---:|---:|
|0|.4643220871|.4221413416|1.1009127381|.9113374996|4|4|
|.05|.4165960476|.3704354536|.9767819646|.7999900039|4|4|
|.10|.3882070942|.3341182928|.8529977963|.6893852724|4|5|
|.15|.3764812636|.3144229993|.729736637|.5799484293|4|5|
|.20|.3748261043|.310812702|.6073170202|.4724916791|6|7|
|.25|.3808831249|.3228632281|.5296881157|.3984450983|6|6|
|.30|.3949017009|.3495905287|.5819084622|.4670791634|7|6|

Freeze candidates for subsequent non-July evaluation: PV0 same-fleet baseline, PV2 unadjusted, PV2-D20 (development mean NRMSE winner), PV2-D25 (development worst-region NRMSE winner). No region-specific tuning. These are empirical output derates, not measured physical losses; they may absorb fleet timing, reporting scope, curtailment and model errors. No admission. Previously examined Jan/Apr/Oct windows are not untouched holdouts for the overall study; use additional unexamined windows for confirmatory evaluation. D1 monthly stock audit pending. Reassess after contemporaneous capacity correction without silently retuning candidates.
