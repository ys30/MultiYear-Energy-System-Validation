"""Common-support PV comparison, holding annual physical parameters fixed."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from paper_a1_e4_pv_kernel import pv_cf
p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);y=p.parse_args().year
a=pd.read_csv("inputs/solar/exact_key_audit.csv",dtype={"gen":str});a=a[a.yr.eq(y)]
audit=pd.read_csv("inputs/pilot/audit.csv",dtype={"gen":str})
a=a.merge(audit[audit.reason.eq("modeled")][["ba","plant","gen"]],on=["ba","plant","gen"],validate="one_to_one")
w=pd.read_csv("inputs/weather/raw_weather.csv");w["time"]=pd.to_datetime(w.time,utc=True)
times=pd.date_range(f"{y}-07-01",periods=168,freq="h",tz="UTC")
grids={(round(float(lat),5),round(float(lon)%360,5)):g.sort_values("time") for (lat,lon),g in w.groupby(["latitude","longitude"])}
rows=[];coverage=[]
for month in ("june","july"):
    m=pd.read_csv(f"inputs/{month}/exact_key_audit.csv",dtype={"gen":str});m=m[m.year.eq(y)]
    m=m[m.ba_annual.eq(m.ba_monthly)&m.tech_annual.eq("Solar Photovoltaic")&m.tech_monthly.eq("Solar Photovoltaic")]
    b=a.merge(m[["plant","gen","mw_annual","mw_monthly"]],on=["plant","gen"],validate="one_to_one")
    if not np.allclose(b.mw,b.mw_annual):raise ValueError("annual MW mismatch")
    for ba,f in b.groupby("ba"):
        am=f.mw.sum();mm=f.mw_monthly.sum()
        if min(am,mm)<=0:raise ValueError("invalid support")
        out=np.zeros((2,3,168))
        for r in f.itertuples(index=False):
            g=grids[(round(r.lat*4)/4,(round(r.lon*4)/4)%360)]
            if not pd.DatetimeIndex(g.time).equals(times):raise ValueError("weather mismatch")
            rad=g.surface_solar_radiation_downwards.to_numpy()
            if (rad< -1).any():raise ValueError("negative radiation")
            ghi=np.maximum(rad,0)/3600;temp=g["2m_temperature"].to_numpy()-273.15
            cf0=np.clip(ghi/1000*(1-.004*(temp+.03*ghi-25)),0,1)
            cf2=pv_cf(times-pd.Timedelta(minutes=30),r.lat,r.lon,ghi,temp,r.mount,r.dc_ac,r.tilt,r.azimuth)
            out+=np.array([cf0,cf2])[:,None,:]*np.array([r.mw,r.mw*mm/am,r.mw_monthly])[None,:,None]
        total=m.loc[m.ba_monthly.eq(ba),"mw_monthly"].sum()
        coverage.append(dict(year=y,month=month,ba=ba,keys=len(f),annual_common_mw=am,monthly_common_mw=mm,monthly_total_mw=total,coverage=mm/total))
        for i,model in enumerate(("PV0","PV2")):
            for j,stock in enumerate(("common_annual","common_scalar","common_monthly")):
                rows.extend(dict(year=y,month=month,ba=ba,model=model,stock=stock,time=t.isoformat(),mw=v,admitted=False) for t,v in zip(times,out[i,j]))
d=Path("results/monthly_pv_common");d.mkdir(parents=True,exist_ok=True)
pd.DataFrame(rows).to_csv(d/"hourly.csv",index=False);c=pd.DataFrame(coverage);c.to_csv(d/"coverage.csv",index=False);print(c.to_json(orient="records"))
