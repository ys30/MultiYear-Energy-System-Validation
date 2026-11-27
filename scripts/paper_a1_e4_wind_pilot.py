"""July W2 pilot with explicit partial fleet coverage and shear sensitivity."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from paper_a1_e4_wind_curve_kernel import capacity_factor,hub_speed
def main():
    p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);y=p.parse_args().year
    a=pd.read_csv("inputs/curves/assignments.csv",dtype={"gen":str})
    c={r["curve"]:r for r in json.loads(Path("inputs/curves/catalog.json").read_text())}
    f=pd.read_csv("inputs/weights/renewable_plant_coordinates.csv",dtype={"gen":str})
    f=f[(f.yr==y)&f.tech.eq("Onshore Wind Turbine")]
    a=f.merge(a[["yr","plant","gen","curve","within_25pct","hub_m"]],on=["yr","plant","gen"],how="left",validate="one_to_one")
    w=pd.read_csv("inputs/weather/raw_weather.csv");w["time"]=pd.to_datetime(w.time,utc=True)
    times=pd.date_range(f"{y}-07-01",periods=168,freq="h",tz="UTC")
    if w.duplicated(["time","latitude","longitude"]).any():raise ValueError("duplicate weather")
    grids={(float(lat),float(lon)%360):g.sort_values("time") for (lat,lon),g in w.groupby(["latitude","longitude"])}
    rows=[];audit=[]
    for ba,b in a.groupby("ba"):
        total=float(b.mw.sum());covered=0.;out=np.zeros((3,len(times)))
        for r in b.itertuples(index=False):
            reason="modeled"
            if str(r.valid).lower()!="true":reason="invalid_coordinates"
            elif str(r.within_25pct).lower()!="true" or r.curve not in c:reason="no_rating_compatible_curve"
            if reason=="modeled":
                g=grids.get((round(r.lat*4)/4,(round(r.lon*4)/4)%360))
                if g is None or not pd.DatetimeIndex(g.time).equals(times):raise ValueError("missing grid")
                curve=c[r.curve]
                for i,alpha in enumerate((.1,1/7,.2)):
                    speed=hub_speed(g["100m_u_component_of_wind"],g["100m_v_component_of_wind"],r.hub_m,alpha)
                    out[i]+=r.mw*capacity_factor(speed,curve["speed"],curve["power_mw"])
                covered+=r.mw
            audit.append(dict(ba=ba,plant=r.plant,gen=r.gen,mw=r.mw,reason=reason))
        for alpha,series in zip((.1,1/7,.2),out):
            rows.extend(dict(time=t.isoformat(),ba=ba,alpha=alpha,modeled_mw=float(v),covered_capacity_mw=covered,total_capacity_mw=total,covered_cf=v/covered if covered else None,partial_fleet_cf=v/total,admitted=False) for t,v in zip(times,series))
    d=Path("results/wind_pilot");d.mkdir(parents=True,exist_ok=True)
    b=pd.DataFrame(rows);b.to_csv(d/"hourly.csv",index=False);pd.DataFrame(audit).to_csv(d/"audit.csv",index=False)
    s=b.groupby(["ba","alpha"]).agg(covered_mw=("covered_capacity_mw","first"),total_mw=("total_capacity_mw","first"),mean_cf=("covered_cf","mean")).reset_index()
    print(s.to_json(orient="records"));(d/"summary.json").write_text(s.to_json(orient="records"))
if __name__=="__main__":main()
