"""Score common support against BA observations; quantify composition separately."""
from pathlib import Path
import pandas as pd
import numpy as np
obs=pd.read_csv(next(Path("inputs/observed").rglob("reconciled.csv")))
obs=obs[obs.series.eq("SUN")].copy();obs["time"]=pd.to_datetime(obs.period,utc=True)
rows=[]
for y in (2024,2025):
    p=pd.read_csv(f"inputs/pv/{y}/hourly.csv");p["time"]=pd.to_datetime(p.time,utc=True)
    for (month,ba,model),g in p.groupby(["month","ba","model"]):
        q=g.pivot(index="time",columns="stock",values="mw").reset_index()
        q=q.merge(obs.loc[obs.ba.eq(ba),["time","api"]],on="time",validate="one_to_one")
        if len(q)!=168 or q.isna().any().any() or q.api.mean()<=0:raise ValueError("invalid cohort")
        a=q.common_annual;s=q.common_scalar;m=q.common_monthly
        r=dict(year=y,month=month,ba=ba,model=model,n=len(q),capacity_effect_mean_mw=(s-a).mean(),composition_effect_mean_mw=(m-s).mean(),composition_rms_mw=np.sqrt(((m-s)**2).mean()),composition_peak_abs_mw=(m-s).abs().max(),admitted=False)
        for name in ("common_annual","common_scalar","common_monthly"):
            r[name+"_nrmse"]=np.sqrt(((q[name]-q.api)**2).mean())/q.api.mean()
        rows.append(r)
d=Path("results/monthly_pv_score");d.mkdir(parents=True,exist_ok=True)
o=pd.DataFrame(rows);o.to_csv(d/"metrics.csv",index=False);print(o.to_json(orient="records"))
