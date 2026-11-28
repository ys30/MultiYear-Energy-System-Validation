"""D2/D3: compare proxy and physical models on exactly the same modeled fleet."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);p.add_argument("--observed",required=True);args=p.parse_args()
f=pd.read_csv("inputs/weights/renewable_plant_coordinates.csv",dtype={"gen":str});f=f[f.yr.eq(args.year)]
w=pd.read_csv("inputs/weather/raw_weather.csv");w["time"]=pd.to_datetime(w.time,utc=True)
if w.duplicated(["time","latitude","longitude"]).any():raise ValueError("duplicate weather")
w["longitude"]=w.longitude%360
speed=np.hypot(w["100m_u_component_of_wind"],w["100m_v_component_of_wind"])
rad=w.surface_solar_radiation_downwards
if (rad< -1).any():raise ValueError("negative radiation")
ghi=rad.clip(lower=0)/3600
w["wind"]=np.where((speed<3)|(speed>=25),0,np.clip((speed**3-27)/(12**3-27),0,1))
w["solar"]=np.clip(ghi/1000*(1-.004*(w["2m_temperature"]-273.15+.03*ghi-25)),0,1)
o=pd.read_csv(args.observed);o["time"]=pd.to_datetime(o.period,utc=True)
rows=[];pairs=[]
for tech,label,series in [("wind","Onshore Wind Turbine","WND"),("solar","Solar Photovoltaic","SUN")]:
    a=pd.read_csv(f"inputs/{tech}/audit.csv",dtype={"gen":str});a=a[a.reason.eq("modeled")]
    g=a.merge(f[f.tech.eq(label)][["ba","plant","gen","lat","lon","mw"]],on=["ba","plant","gen"],validate="one_to_one",suffixes=("_audit",""))
    if len(g)!=len(a) or not np.allclose(g.mw,g.mw_audit):raise ValueError("fleet mismatch")
    g["latitude"]=(g.lat*4).round()/4;g["longitude"]=((g.lon*4).round()/4)%360
    g=g.groupby(["ba","latitude","longitude"],as_index=False).mw.sum()
    j=g.merge(w[["latitude","longitude","time",tech]],on=["latitude","longitude"],validate="many_to_many")
    if len(j)!=168*len(g):raise ValueError("weather coverage mismatch")
    j["proxy_mw"]=j.mw*j[tech]
    b=j.groupby(["ba","time"],as_index=False).agg(proxy_mw=("proxy_mw","sum"),capacity=("mw","sum"))
    h=pd.read_csv(f"inputs/{tech}/hourly.csv");h["time"]=pd.to_datetime(h.time,utc=True)
    if tech=="wind":h=h[np.isclose(h.alpha,1/7)]
    b=b.merge(h,on=["ba","time"],validate="one_to_one")
    if len(b)!=len(h) or not np.allclose(b.capacity,b.covered_capacity_mw):raise ValueError("physical coverage mismatch")
    b=b.merge(o[o["series"].eq(series)][["ba","time","api"]],on=["ba","time"],validate="one_to_one").dropna(subset=["api"])
    b["tech"]=tech;pairs.append(b)
    for ba,k in b.groupby("ba"):
        for model,col in [("proxy","proxy_mw"),("physical","modeled_mw")]:
            e=k[col]-k.api
            rows.append(dict(year=args.year,ba=ba,tech=tech,model=model,n=len(k),coverage=float(k.capacity.iloc[0]/k.total_capacity_mw.iloc[0]),relative_bias=float(e.sum()/k.api.sum()) if k.api.sum()!=0 else None,rmse=float(np.sqrt((e**2).mean())),mae=float(e.abs().mean()),corr=float(k[col].corr(k.api)),admitted=False))
d=Path("results/same_fleet");d.mkdir(parents=True,exist_ok=True);s=pd.DataFrame(rows);s.to_csv(d/"metrics.csv",index=False);pd.concat(pairs).to_csv(d/"paired.csv",index=False);print(s.to_json(orient="records"))
