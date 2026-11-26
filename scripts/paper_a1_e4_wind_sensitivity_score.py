"""Score all sensitivity curves against observations; diagnostic only."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
def main():
    p=argparse.ArgumentParser();p.add_argument("--wind",type=Path,required=True);p.add_argument("--weights",type=Path,required=True);p.add_argument("--observed",type=Path,required=True);p.add_argument("--year",type=int,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    f=pd.read_csv(a.wind);w=pd.read_csv(a.weights);w=w[(w.yr==a.year)&w.tech.eq("Onshore Wind Turbine")].groupby("ba",as_index=False).mw.sum()
    f=f.merge(w,on="ba",validate="many_to_one");f["proxy"]=f.cf*f.mw;f["period"]=pd.to_datetime(f.time,utc=True)
    o=pd.read_csv(a.observed);o=o[o.series.eq("WND")].copy();o["period"]=pd.to_datetime(o.period,utc=True)
    f=f.merge(o[["period","ba","api"]],on=["period","ba"],how="left",validate="many_to_one")
    rows=[]
    for (ba,r,m),g in f.groupby(["ba","rated","speed_multiplier"]):
        if len(g)!=168 or g.api.isna().any():raise ValueError("incomplete observed comparison")
        e=g.proxy-g.api
        rows.append(dict(year=a.year,ba=ba,rated=r,speed_multiplier=m,n=len(g),bias=float(e.mean()),relative_bias=float(e.mean()/g.api.mean()),mae=float(e.abs().mean()),rmse=float(np.sqrt((e**2).mean())),correlation=float(g.proxy.corr(g.api))))
    q=pd.DataFrame(rows)
    if len(q)!=105:raise ValueError("incomplete parameter grid")
    q.to_csv(a.output_dir/"scores.csv",index=False)
    s=q.groupby(["rated","speed_multiplier"]).agg(mean_abs_relative_bias=("relative_bias",lambda x:x.abs().mean()),worst_abs_relative_bias=("relative_bias",lambda x:x.abs().max()),mean_correlation=("correlation","mean")).reset_index()
    s.to_csv(a.output_dir/"common_parameter_scores.csv",index=False)
    print(json.dumps(dict(year=a.year,admitted=False,diagnostic_only=True,common=s.to_dict("records"))))
if __name__=="__main__":main()
