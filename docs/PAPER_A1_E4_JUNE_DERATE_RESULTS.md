# June stock and joint derate diagnostic
CI 46117933740 and 46117934119 succeeded. June OP stock reconciliation 28 groups. Solar annual minus June MW by BA AZPS,CISO,ERCO,IPCO,PACW,PNM,PSCO: 2024 [152.9,1864.7,4685.7,2.6,10.9,500,171.5]; 2025 [0,1305.1,4616.5,-0.4,12.7,419.4,660.6]. Totals 7388.3 and 7013.9 MW. June is a near-period snapshot, not exact hourly availability.
Joint diagnostic 84 groups, 14 BA-years per configuration:
|Stock|Loss|Mean NRMSE|Worst NRMSE|
|---|---:|---:|---:|
|annual|0|.4432317143|1.1009127381|
|annual|.20|.3428194031|.6073170202|
|annual|.25|.3518731765|.5296881157|
|july_scaled|0|.3405735652|.6657056684|
|july_scaled|.20|.3265358270|.6210676880|
|july_scaled|.25|.3621804614|.6655452793|
Scalar correction and derate are multiplicative; observed skill cannot uniquely identify physical losses. July development window, no admission. Next: June/July exact-key common-support fleet reweighting, independent windows.
