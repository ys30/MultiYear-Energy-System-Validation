"""Score frozen D5 candidates on identical observed hours."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);p.add_argument("--month",type=int,required=True);a=p.parse_args()
b=pd.read_csv("results/same_fleet/paired.csv");rows=[]
for (tech,ba),g in b.groupby(["tech","ba"]):
    candidates={"W0":g.proxy_mw,"W2":g.modeled_mw} if tech=="wind" else {"PV0":g.proxy_mw,"PV2":g.modeled_mw,"PV2-D20":.8*g.modeled_mw,"PV2-D25":.75*g.modeled_mw}
    if g.api.mean()<=0 or len(g)<1:raise ValueError("invalid observations")
    for model,v in candidates.items():
        e=v-g.api
        if not np.isfinite(e).all():raise ValueError("nonfinite")
        rows.append(dict(year=a.year,month=a.month,ba=ba,tech=tech,model=model,n=len(g),missing=168-len(g),coverage=g.covered_capacity_mw.iloc[0]/g.total_capacity_mw.iloc[0],nrmse=np.sqrt((e**2).mean())/g.api.mean(),mae=e.abs().mean(),bias=e.mean(),corr=v.corr(g.api),admitted=False))
o=pd.DataFrame(rows)
if len(o)!=42:raise ValueError("missing cohort")
d=Path("results/d5");d.mkdir(parents=True,exist_ok=True);o.to_csv(d/"metrics.csv",index=False);print(o.to_json(orient="records"))
