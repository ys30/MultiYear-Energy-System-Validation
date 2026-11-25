"""Export paired scenario differences for the seven-state pilot; no dispatch assumptions."""
import argparse,csv,json
from pathlib import Path
from collections import defaultdict
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    states={"CA","TX","AZ","CO","NM","ID","WY"}
    scenarios={"S0_pair_baseline","S1_unmatched_only","S2_full_OP"}
    groups=defaultdict(dict)
    with (d/"e4_capacity_scenarios.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r["state"] not in states:continue
            k=(int(r["year_b"]),r["state"],r["technology"])
            if r["scenario"] in groups[k]:raise ValueError("Duplicate scenario key")
            groups[k][r["scenario"]]=float(r["capacity_mw"])
    result=[]
    for (year,state,tech),g in sorted(groups.items()):
        if set(g)!=scenarios:raise ValueError("Incomplete scenario group")
        a,b,c=(g[s] for s in ("S0_pair_baseline","S1_unmatched_only","S2_full_OP"))
        result.append(dict(year=year,state=state,technology=tech,S0_mw=a,S1_mw=b,S2_mw=c,S2_minus_S1_mw=round(c-b,6)))
    if {(r["year"],r["state"]) for r in result}!={(y,s) for y in (2024,2025) for s in states}:raise ValueError("Missing pilot state/year")
    with (d/"e4_pilot_capacity_differences.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    print(json.dumps({"state_year_groups":14,"planned_scenario_runs":42,"technology_groups":len(result),"dispatch_ready":False}))
if __name__=="__main__":main()
