# D1 scalar stock diagnostic
CI 46117443643 success; 112 groups, 168 hours each. Equal BA-year mean NRMSE:
|Model|Annual|July scalar|
|---|---:|---:|
|PV0|0.4396766826|0.4491203799|
|PV2|0.4432317143|0.3405735652|
|W0|0.7247522667|0.7255472832|
|W2|0.6905017515|0.6909920989|
PV2 relative reduction 23.16%; descriptive difference-in-differences in NRMSE = -0.1121018464. PV2 improves 8/14, worsens 3/14, unchanged 3/14. PNM 2024 bias .773096 -> .276152; PSCO 2025 .626855 -> .243458. ERCO 2024 .002890 -> -.199813, 2025 -.003838 -> -.153828. Aggregate scaling preserves annual spatial composition and applies full-stock ratio to covered fleet. Not monthly reconstruction, causal identification, or admission. July month-end is not early July availability. Next: June source and exact-key matched fleet.
