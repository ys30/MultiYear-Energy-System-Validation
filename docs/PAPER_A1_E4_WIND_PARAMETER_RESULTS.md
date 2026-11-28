# Wind parameter coverage audit
Pinned run 45900246129; repeat 45901610578 produced identical aggregate results.
2024: 420/424 matched, 53717.1 MW total, 53334.1 MW matched.
2025: 430/434 matched, 55624.8 MW total, 55241.8 MW matched.
All matched rows agree in MW within 0.01 MW, have nonempty predominant manufacturer/model, positive hub height and positive integer turbine count. These are preliminary presence checks, not validated physical ranges or curve matches.
ERCO unmatched 3 rows / 340 MW each year; PACW 1 row / 43 MW each year. Do not infer identical physical keys from aggregate counts. Investigate status and source scope. No automatic fuzzy join.
Next: inventory exact manufacturer/model pairs, check placeholder strings and physical ranges, compare against versioned turbine curve library; preserve unmatched MW explicitly. Design wind speed is not rated speed. No CF admitted. PR remains unmerged.
