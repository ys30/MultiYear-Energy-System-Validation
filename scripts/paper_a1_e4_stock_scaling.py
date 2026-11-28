"""Aggregate stock scaling diagnostic, not monthly fleet reconstruction."""
from pathlib import Path
import pandas as pd
import numpy as np
s=pd.read_csv("inputs/stock/summary.csv")
rows=[]
for y in (2024,2025):
    p=pd.read_csv(f"inputs/fleet/{y}/paired.csv")
    for (ba,tech),g in p.groupby(["ba","tech"]):
        label={"wind":"Onshore Wind Turbine","solar":"Solar Photovoltaic"}[tech]
        r=s[(s.year==y)&(s.ba==ba)&(s.tech==label)].iloc[0]
        ratio=r.july_mw/r.annual_mw
        if len(g)!=168 or g.api.isna().any() or g.api.mean()<=0:raise ValueError("invalid paired cohort")
        for model,col in [("proxy","proxy_mw"),("physical","modeled_mw")]:
            for stock,factor in [("annual",1.),("july_scalar",ratio)]:
                pred=g[col]*factor;e=pred-g.api
                rows.append(dict(year=y,ba=ba,tech=tech,model=model,stock=stock,ratio=ratio,n=len(g),bias=e.sum()/g.api.sum(),nrmse=np.sqrt((e**2).mean())/g.api.mean(),admitted=False))
d=Path("results/stock_scaling");d.mkdir(parents=True,exist_ok=True)
o=pd.DataFrame(rows);o.to_csv(d/"metrics.csv",index=False)
print(o.groupby(["tech","model","stock"]).nrmse.mean().reset_index().to_json(orient="records"))
print(o.to_json(orient="records"))
