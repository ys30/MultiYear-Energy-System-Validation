"""Wind common-support capacity/composition diagnostic; no resource admission."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from paper_a1_e4_wind_curve_kernel import capacity_factor,hub_speed
p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);y=p.parse_args().year
a=pd.read_csv("inputs/weights/renewable_plant_coordinates.csv",dtype={"gen":str})
a=a[(a.yr==y)&a.tech.eq("Onshore Wind Turbine")]
c=pd.read_csv("inputs/curves/assignments.csv",dtype={"gen":str})
a=a.merge(c[["yr","plant","gen","curve","hub_m","within_25pct"]],on=["yr","plant","gen"],validate="one_to_one")
catalog={r["curve"]:r for r in json.loads(Path("inputs/curves/catalog.json").read_text())}
a=a[a.valid.eq(True)&a.within_25pct.eq(True)&a.curve.isin(catalog)]
w=pd.read_csv("inputs/weather/raw_weather.csv");w["time"]=pd.to_datetime(w.time,utc=True)
times=pd.date_range(f"{y}-07-01",periods=168,freq="h",tz="UTC")
if w.duplicated(["time","latitude","longitude"]).any():raise ValueError("duplicate weather")
grids={(round(float(lat),5),round(float(lon)%360,5)):g.sort_values("time") for (lat,lon),g in w.groupby(["latitude","longitude"])}
rows=[];coverage=[]
for month in ("june","july"):
    full=pd.read_csv(f"inputs/{month}/exact_key_audit.csv",dtype={"gen":str});full=full[full.year.eq(y)]
    m=full[full.ba_annual.eq(full.ba_monthly)&full.tech_annual.eq("Onshore Wind Turbine")&full.tech_monthly.eq("Onshore Wind Turbine")]
    b=a.merge(m[["plant","gen","mw_annual","mw_monthly"]],on=["plant","gen"],validate="one_to_one")
    if not np.allclose(b.mw,b.mw_annual):raise ValueError("annual MW mismatch")
    if set(b.ba)!=set(a.ba):raise ValueError("missing BA")
    for ba,f in b.groupby("ba"):
        am=f.mw.sum();mm=f.mw_monthly.sum()
        total=full.loc[full.ba_monthly.eq(ba)&full.tech_monthly.eq("Onshore Wind Turbine"),"mw_monthly"].sum()
        if min(am,mm,total)<=0 or mm>total+1e-6:raise ValueError("invalid support")
        out=np.zeros((2,3,168))
        for r in f.itertuples(index=False):
            g=grids[(round(r.lat*4)/4,(round(r.lon*4)/4)%360)]
            if not pd.DatetimeIndex(g.time).equals(times):raise ValueError("weather mismatch")
            u=g["100m_u_component_of_wind"].to_numpy();v=g["100m_v_component_of_wind"].to_numpy()
            speed=np.hypot(u,v)
            cf0=np.where((speed>=3)&(speed<25),np.clip((speed**3-3**3)/(12**3-3**3),0,1),0)
            curve=catalog[r.curve];cf2=capacity_factor(hub_speed(u,v,r.hub_m,1/7),curve["speed"],curve["power_mw"])
            out+=np.array([cf0,cf2])[:,None,:]*np.array([r.mw,r.mw*mm/am,r.mw_monthly])[None,:,None]
        coverage.append(dict(year=y,month=month,ba=ba,keys=len(f),annual_common_mw=am,monthly_common_mw=mm,monthly_total_mw=total,coverage=mm/total))
        for i,model in enumerate(("W0","W2")):
            for j,stock in enumerate(("common_annual","common_scalar","common_monthly")):
                rows.extend(dict(year=y,month=month,ba=ba,model=model,stock=stock,time=t.isoformat(),mw=v,admitted=False) for t,v in zip(times,out[i,j]))
d=Path("results/monthly_wind_common");d.mkdir(parents=True,exist_ok=True)
pd.DataFrame(rows).to_csv(d/"hourly.csv",index=False);c=pd.DataFrame(coverage);c.to_csv(d/"coverage.csv",index=False);print(c.to_json(orient="records"))
