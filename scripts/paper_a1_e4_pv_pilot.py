"""July PV2 pilot. Report missing capacity explicitly; no formal admission."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from paper_a1_e4_pv_kernel import pv_cf
def main():
    p=argparse.ArgumentParser();p.add_argument("--year",type=int,required=True);p.add_argument("--month",type=int,default=7,choices=range(1,13));args=p.parse_args();y=args.year;month=args.month
    a=pd.read_csv("inputs/solar/exact_key_audit.csv",dtype={"gen":str});a=a[a.yr.eq(y)]
    w=pd.read_csv("inputs/weather/raw_weather.csv");w["time"]=pd.to_datetime(w.time,utc=True)
    if w.duplicated(["time","latitude","longitude"]).any():raise ValueError("duplicate weather")
    times=pd.DatetimeIndex(sorted(w.time.unique()))
    if len(times)!=168 or not times.equals(pd.date_range(f"{y}-{month:02d}-01",periods=168,freq="h",tz="UTC")):raise ValueError("unexpected weather window")
    grids={(round(float(lat),5),round(float(lon)%360,5)):g.sort_values("time") for (lat,lon),g in w.groupby(["latitude","longitude"])}
    rows=[];audit=[]
    for ba,f in a.groupby("ba"):
        total=f.mw.sum();covered=0.;out=np.zeros(len(times))
        for r in f.itertuples(index=False):
            reason=None
            if not all(pd.notna(v) and str(v).lower()=="true" for v in (r.valid,r.matched,r.mw_agree,r.dc_valid)):reason="invalid_coordinates_or_rating"
            elif r.mount not in ("single","dual","fixed","eastwest"):reason="unresolved_mount"
            elif r.mount in ("fixed","eastwest") and not 0<=r.tilt<=90:reason="missing_tilt"
            elif r.mount=="fixed" and not 0<=r.azimuth<=360:reason="missing_azimuth"
            if reason is None:
                key=(round(r.lat*4)/4,(round(r.lon*4)/4)%360)
                g=grids.get(key)
                if g is None or not pd.DatetimeIndex(g.time).equals(times):raise ValueError("missing weather grid")
                rad=g.surface_solar_radiation_downwards.to_numpy()
                if (rad< -1).any():raise ValueError("negative radiation")
                cf=pv_cf(times-pd.Timedelta(minutes=30),r.lat,r.lon,np.maximum(rad,0)/3600,g["2m_temperature"].to_numpy()-273.15,r.mount,r.dc_ac,r.tilt,r.azimuth)
                out+=r.mw*cf;covered+=r.mw
            audit.append(dict(ba=ba,plant=r.plant,gen=r.gen,mw=r.mw,reason=reason or "modeled"))
        if covered<=0:raise ValueError("no modeled capacity")
        rows.extend(dict(time=t.isoformat(),ba=ba,modeled_mw=float(v),covered_capacity_mw=covered,total_capacity_mw=total,covered_cf=v/covered,partial_fleet_cf=v/total,admitted=False) for t,v in zip(times,out))
    d=Path("results/pv_pilot");d.mkdir(parents=True,exist_ok=True)
    b=pd.DataFrame(rows);b.to_csv(d/"hourly.csv",index=False);pd.DataFrame(audit).to_csv(d/"audit.csv",index=False)
    summary=b.groupby("ba").agg(covered_mw=("covered_capacity_mw","first"),total_mw=("total_capacity_mw","first"),mean_cf=("covered_cf","mean"),peak_mw=("modeled_mw","max")).reset_index()
    print(summary.to_json(orient="records"));(d/"summary.json").write_text(summary.to_json(orient="records"))
if __name__=="__main__":main()
