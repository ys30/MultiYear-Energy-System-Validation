"""D4: predeclared uniform PV output derates; July development diagnostics only."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);a=p.parse_args()
f=pd.read_csv("inputs/same/paired.csv")
f=f[f.tech.eq("solar")].copy()
rows=[]
for ba,g in f.groupby("ba"):
    if len(g)!=168 or g.time.duplicated().any():raise ValueError("unexpected paired coverage")
    if not np.isfinite(g[["api","modeled_mw","proxy_mw"]]).all().all():raise ValueError("nonfinite input")
    for loss in (0,.05,.10,.15,.20,.25,.30):
        v=g.modeled_mw*(1-loss);e=v-g.api
        rows.append(dict(year=a.year,ba=ba,loss=loss,n=len(g),relative_bias=float(e.sum()/g.api.sum()),rmse=float(np.sqrt((e**2).mean())),normalized_rmse=float(np.sqrt((e**2).mean())/g.api.mean()),proxy_rmse=float(np.sqrt(((g.proxy_mw-g.api)**2).mean())),corr=float(v.corr(g.api)),admitted=False))
s=pd.DataFrame(rows)
d=Path("results/loss_sensitivity");d.mkdir(parents=True,exist_ok=True)
s.to_csv(d/"metrics.csv",index=False)
summary=s.groupby("loss").agg(mean_nrmse=("normalized_rmse","mean"),worst_nrmse=("normalized_rmse","max")).reset_index()
summary["mean_abs_relative_bias"]=s.groupby("loss").relative_bias.apply(lambda x:x.abs().mean()).to_numpy()
summary["wins_vs_proxy"]=s.assign(win=s.rmse<s.proxy_rmse).groupby("loss").win.sum().to_numpy()
summary.to_csv(d/"summary.csv",index=False);print(summary.to_json(orient="records"))
