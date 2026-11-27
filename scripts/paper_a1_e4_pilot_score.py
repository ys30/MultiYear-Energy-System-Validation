"""Compare partial-fleet pilots against BA observations; diagnostic only."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
p=argparse.ArgumentParser();p.add_argument("--observed",required=True);p.add_argument("--year",type=int,required=True);args=p.parse_args()
o=pd.read_csv(args.observed);o["time"]=pd.to_datetime(o.period,utc=True)
rows=[]
for tech in ("wind","solar"):
    a=pd.read_csv(f"inputs/{tech}/hourly.csv");a["time"]=pd.to_datetime(a.time,utc=True)
    a["alpha"]=a.alpha if "alpha" in a else "PV2"
    obs=o[o["series"].eq("WND" if tech=="wind" else "SUN")][["ba","time","api"]]
    for (ba,alpha),g in a.groupby(["ba","alpha"]):
        if len(g)!=168 or g.time.duplicated().any():raise ValueError("invalid pilot")
        for shift in (-1,0,1):
            h=g.copy();h.time+=pd.Timedelta(hours=shift)
            h=h.merge(obs,on=["ba","time"],validate="one_to_one").dropna(subset=["api"])
            if h.empty:raise ValueError("no observed overlap")
            e=h.modeled_mw-h.api
            rows.append(dict(year=args.year,tech=tech,ba=ba,alpha=str(alpha),shift=shift,n=len(h),coverage=float(g.covered_capacity_mw.iloc[0]/g.total_capacity_mw.iloc[0]),bias=float(e.mean()),relative_bias=float(e.sum()/h.api.sum()) if h.api.sum()!=0 else None,mae=float(e.abs().mean()),rmse=float(np.sqrt((e**2).mean())),corr=float(h.modeled_mw.corr(h.api)),admitted=False))
d=Path("results/pilot_score");d.mkdir(parents=True,exist_ok=True);s=pd.DataFrame(rows);s.to_csv(d/"metrics.csv",index=False);print(s[s["shift"].eq(0)].to_json(orient="records"))
