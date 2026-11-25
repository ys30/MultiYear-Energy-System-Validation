"""Construct aggregate capacity counterfactuals, not physical fleet reconstructions."""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    with (d/"e3_op_stock_by_state_technology.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    groups=defaultdict(lambda:[0.,0.,0.])
    for r in rows:
        k=(int(r["year_a"]),r["state"],r["technology"])
        a,b=float(r["earlier_mw"]),float(r["later_mw"])
        g=groups[k];g[0]+=a;g[1]+=b
        if r["category"] in ("earlier_only","later_only"):g[2]+=b-a
    result=[]
    for (year,state,tech),(a,b,delta) in sorted(groups.items()):
        for scenario,mw in [("S0_pair_baseline",a),("S1_unmatched_only",a+delta),("S2_full_OP",b)]:
            if mw < -1e-6:raise ValueError("Negative scenario capacity")
            result.append(dict(year_a=year,year_b=year+1,state=state,technology=tech,scenario=scenario,capacity_mw=round(max(0,mw),6)))
    with (d/"e4_capacity_scenarios.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    totals=defaultdict(float)
    for r in result:totals[(r["year_a"],r["scenario"])]+=r["capacity_mw"]
    print(json.dumps([dict(year_a=y,scenario=s,capacity_mw=v) for (y,s),v in sorted(totals.items())]))
if __name__=="__main__":main()
