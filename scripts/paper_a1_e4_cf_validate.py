"""Compare exploratory resource proxy to observed EIA930 generation, no calibration."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
def main():
    p=argparse.ArgumentParser();p.add_argument("--cf",type=Path,required=True);p.add_argument("--weights",type=Path,required=True);p.add_argument("--observed",type=Path,required=True);p.add_argument("--year",type=int,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    f=pd.read_csv(a.cf);w=pd.read_csv(a.weights);
    w=w[w.yr==a.year].groupby(["ba","tech"],as_index=False).mw.sum()
    f=f.merge(w,on=["ba","tech"],validate="many_to_one");f["proxy_mw"]=f.cf*f.mw
    f["series"]=np.where(f.tech.eq("Solar Photovoltaic"),"SUN","WND")
    f["period"]=pd.to_datetime(f.time,utc=True)
    o=pd.read_csv(a.observed);o["period"]=pd.to_datetime(o.period,utc=True)
    o=o[o.series.isin(["SUN","WND"])][["period","ba","series","api"]]
    rows=[];pairs=[]
    for shift in (-1,0,1):
        q=f.copy();q.period+=pd.Timedelta(hours=shift)
        q=q.merge(o,on=["period","ba","series"],how="left",validate="one_to_one");q["shift_hours"]=shift;pairs.append(q)
        for (ba,s),g in q.groupby(["ba","series"]):
            v=g.dropna(subset=["api"]);e=v.proxy_mw-v.api
            rows.append(dict(year=a.year,ba=ba,series=s,shift_hours=shift,n=len(v),bias_mw=float(e.mean()),mae_mw=float(e.abs().mean()),rmse_mw=float(np.sqrt((e**2).mean())),correlation=float(v.proxy_mw.corr(v.api)),observed_mean_mw=float(v.api.mean()),proxy_mean_mw=float(v.proxy_mw.mean())))
    pd.concat(pairs).to_csv(a.output_dir/"paired.csv",index=False)
    pd.DataFrame(rows).to_csv(a.output_dir/"metrics.csv",index=False);print(json.dumps(rows))
if __name__=="__main__":main()
