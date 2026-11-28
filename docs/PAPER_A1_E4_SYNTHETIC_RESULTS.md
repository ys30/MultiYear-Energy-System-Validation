# E4-P0 verified synthetic dispatch results
CI run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/45665197106
84 optimal 24-hour solves, seven states, two target years, three capacity scenarios, storage off/on. All passed hourly balance checks.
S2 vs S1 objective changes (%), no storage / storage:
|State|2024 off|2024 on|2025 off|2025 on|
|---|---:|---:|---:|---:|
|AZ|-47.4|-4.5|12.6|-2.5|
|CA|0.1|-8.6|-1.7|-2.6|
|CO|6.2|4.0|-9.6|-12.9|
|ID|-15.3|-16.7|5.1|-11.4|
|NM|-9.7|-21.5|-1.8|-10.4|
|TX|-15.1|-57.9|6.8|-29.1|
|WY|-42.2|-42.2|-43.4|-43.4|
Storage changes the sign of the S2-S1 objective contrast in four state-year pairs (CA 2024, AZ/ID/TX 2025). The objective includes a stylized slack penalty, not observed production costs. Synthetic demand is anchored to S2 non-storage nameplate capacity; availability, costs and storage durations are assumed. These are integration tests, not historical adequacy estimates.
## Historical experiment admission
Do not attach BA demand to state capacity without an independently verified spatial mapping. Preferred route: use plant-year BA crosswalk to recompute side-specific BA/technology OP stock accounting, then match EIA-930 BA demand and observed weather-derived profiles. Preserve unknown BA and crosswalk changes explicitly. Verify UTC calendar completeness, no duplicate hours, and storage energy capacity or declared sensitivity bounds. Keep state pilot separate from BA experiment. No physical generator lineage claims.
