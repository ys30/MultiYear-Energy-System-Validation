"""Aggregate stock scaling diagnostic, not reconstructed monthly fleet."""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);a=p.parse_args()
s=pd.read_csv("inputs/stock/summary.csv")
s=s[(s.year==a.year)&s.tech.eq("Solar Photovoltaic")]
f=pd.read_csv("inputs/same/paired.csv");f=f[f.tech.eq("solar")]
f=f.merge(s[["ba","annual_mw","july_mw"]],on="ba",validate="many_to_one")
if len(f)!=1176 or f.duplicated(["ba","time"]).any():raise ValueError("coverage")
rows=[]
for ba,g in f.groupby("ba"):
    if not np.isfinite(g[["annual_mw","july_mw","modeled_mw","api"]]).all().all() or g.api.mean()<=0 or g.annual_mw.min()<=0:raise ValueError("invalid input")
    ratio=g.july_mw.iloc[0]/g.annual_mw.iloc[0]
    for stock,k in [("annual",1),("july_scaled",ratio)]:
        for loss in (0,.20,.25):
            v=g.modeled_mw*k*(1-loss);e=v-g.api
            rows.append(dict(year=a.year,ba=ba,stock=stock,loss=loss,stock_ratio=ratio,n=len(g),bias=float(e.sum()/g.api.sum()),nrmse=float(np.sqrt((e**2).mean())/g.api.mean()),rmse=float(np.sqrt((e**2).mean())),admitted=False))
d=Path("results/stock_derate");d.mkdir(parents=True,exist_ok=True)
r=pd.DataFrame(rows);r.to_csv(d/"metrics.csv",index=False)
q=r.groupby(["stock","loss"]).agg(mean_nrmse=("nrmse","mean"),worst_nrmse=("nrmse","max")).reset_index()
q.to_csv(d/"summary.csv",index=False);print(q.to_json(orient="records"));print(r.to_json(orient="records"))
