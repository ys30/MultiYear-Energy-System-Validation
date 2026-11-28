"""Synthetic 24-hour PyPSA integration test; NOT historical dispatch or adequacy."""
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path
import pandas as pd
import pypsa
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    groups=defaultdict(list)
    with (d/"e4_pilot_capacity_differences.csv").open(newline="") as f:
        for r in csv.DictReader(f):groups[(r["year"],r["state"])].append(r)
    result=[]
    for (year,state),rows in sorted(groups.items()):
        # Common synthetic demand, anchored to full OP non-storage capacity.
        def storage(t):return t in ("Batteries","Hydroelectric Pumped Storage")
        base=sum(float(r["S2_mw"]) for r in rows if not storage(r["technology"]))
        demand=[base*(0.55+0.15*math.cos((h-18)*math.pi/12)) for h in range(24)]
        for scenario in ("S0","S1","S2"):
            n=pypsa.Network()
            n.set_snapshots(pd.date_range(f"{year}-07-01",periods=24,freq="h"))
            n.add("Bus","state")
            n.add("Load","synthetic",bus="state",p_set=demand)
            excluded=0.
            for i,r in enumerate(rows):
                t=r["technology"];mw=float(r[scenario+"_mw"])
                if storage(t):excluded+=mw;continue
                if mw<=0:continue
                if t=="Solar Photovoltaic":cost=2;avail=[max(0,math.sin((h-6)*math.pi/12)) for h in range(24)]
                elif "Wind" in t:cost=2;avail=0.35
                elif t=="Nuclear":cost=15;avail=0.9
                elif "Coal" in t:cost=40;avail=0.85
                elif "Natural Gas" in t:cost=65;avail=0.9
                elif "Hydroelectric" in t:cost=9;avail=0.45
                else:cost=90;avail=0.8
                n.add("Generator",f"g{i}",bus="state",p_nom=mw,p_max_pu=avail,marginal_cost=cost)
            n.add("Generator","slack",bus="state",p_nom=max(demand),marginal_cost=10000)
            status,condition=n.optimize(solver_name="highs",log_to_console=False)
            if (status,condition)!=("ok","optimal"):raise RuntimeError((year,state,scenario,status,condition))
            if (n.generators_t.p.sum(axis=1)-pd.Series(demand,index=n.snapshots)).abs().max()>0.001:raise ValueError("Energy balance")
            result.append(dict(year=year,state=state,scenario=scenario,synthetic_demand_mwh=sum(demand),objective=float(n.objective),synthetic_slack_mwh=float(n.generators_t.p["slack"].sum()),excluded_storage_mw=excluded,solver_status=condition))
    if len(result)!=42:raise ValueError("Incomplete pilot")
    with (d/"e4_synthetic_dispatch_smoke.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    print(json.dumps(result))
if __name__=="__main__":main()
