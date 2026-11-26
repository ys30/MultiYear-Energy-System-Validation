# Verified battery scenario accounting
Run 45764005033 succeeded. 56 metric rows, 168 scenario slots, 162 numeric. AZPS 2024 S0/S1 MWh and charge/discharge MW remain null due to one invalid 2023 rating (50 MW). Do not impute in primary results.
2025 selected BA MWh S0/S1/S2:
AZPS 2142.6/2142.6/8777.4
CISO 39966.4/40358.6/53186.7
ERCO 11498/13235.6/21253.8
IPCO 160/160/1832
PACW 0/0/0
PNM 2683.7/2683.7/3739
PSCO 964.6/1064.6/1104.6
Totals 57415.3/59645.1/89893.5 MWh. S2-S1 30248.4 MWh; 93.13% of S2-S0. This is matched-key contribution, not measurement error or causal effect. S1 uses all-status key membership.
Next resource gate: Project B observed renewable generation is not availability. Project C2 ERA5 heat proxies are not wind/solar CF. Reuse source access only; use fixed spatial weights across scenarios, plant coordinates and independent weather, explicit turbine/PV conversion, UTC interval alignment and no observed generation divided by scenario capacity. Validate complete hourly coverage and physical bounds before dispatch.
Latest demand retry 45764004933 timed out; previously successful pinned artifacts 45711142520 and 45715836606 remain the demand evidence. National rerun 45764004944 cancelled; no replacement of frozen evidence.
