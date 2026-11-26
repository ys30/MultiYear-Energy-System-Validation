"""Exploratory grid-to-BA CF conversion; radiation interval assumption not yet admitted."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--weights",type=Path,required=True);p.add_argument("--year",type=int,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();d=a.output_dir;d.mkdir(parents=True,exist_ok=True)
    f=pd.read_csv(a.raw);w=pd.read_csv(a.weights);w=w[w.yr==a.year]
    if f.duplicated(["time","latitude","longitude"]).any():raise ValueError("duplicate weather key")
    rad=f.surface_solar_radiation_downwards
    if (rad < -1).any():raise ValueError("material negative radiation")
    ghi=rad.clip(lower=0)/3600
    speed=np.hypot(f["100m_u_component_of_wind"],f["100m_v_component_of_wind"])
    temp=f["2m_temperature"]-273.15
    f["wind_cf"]=np.where((speed<3)|(speed>=25),0,np.clip((speed**3-27)/(12**3-27),0,1))
    f["solar_cf"]=np.clip(ghi/1000*(1-.004*(temp+.03*ghi-25)),0,1)
    j=f.merge(w,left_on=["latitude","longitude"],right_on=["grid_lat","grid_lon"],how="inner")
    j["cf"]=np.where(j.tech.eq("Solar Photovoltaic"),j.solar_cf,j.wind_cf)
    j["weighted"]=j.cf*j.weight
    g=j.groupby(["time","ba","tech"],as_index=False).agg(cf=("weighted","sum"),weight_sum=("weight","sum"))
    if len(g)!=168*14 or not np.allclose(g.weight_sum,1) or not g.cf.between(0,1+1e-9).all():raise ValueError("CF coverage or bounds")
    g.to_csv(d/"exploratory_cf.csv",index=False)
    r=g.groupby(["ba","tech"]).cf.agg(["min","mean","max"]).reset_index().to_dict("records")
    m=dict(year=a.year,rows=len(g),negative_radiation_clipped=int((rad<0).sum()),radiation_assumption="preceding one-hour accumulation, not yet source-verified",solar_model="horizontal irradiance temperature proxy, not calibrated PV",admitted=False,summary=r)
    (d/"cf_manifest.json").write_text(json.dumps(m,indent=2));print(json.dumps(m))
if __name__=="__main__":main()
