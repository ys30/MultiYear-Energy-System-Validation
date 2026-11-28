# D1 stock × derate diagnostic
Run 46084160972 succeeded both years. 84 metrics, July development only. Aggregate scaling multiplies partial-fleet PV2 by total BA July/annual stock ratio, not generator reconstruction.
| Stock | Derate | Mean NRMSE 2024 | Mean NRMSE 2025 | Worst 2024 | Worst 2025 |
|---|---:|---:|---:|---:|---:|
|annual|0|.4643220871|.4221413416|1.1009127381|.9113374996|
|annual|.20|.3748261043|.310812702|.6073170202|.4724916791|
|annual|.25|.3808831249|.3228632281|.5296881157|.3984450983|
|July scaled|0|.3670658955|.314081235|.6657056684|.5214102289|
|July scaled|.20|.3495371275|.3035345265|.621067688|.4956101769|
|July scaled|.25|.3801214364|.3442394865|.6655452793|.5554543226|
July scaling alone rivals annual D20. Combined D20 minimizes mean but annual D25 minimizes worst-region NRMSE in both years. Nonadditive diagnostic improvements are not causal attribution. No model admitted. June snapshots and generator-level reconstruction required.
