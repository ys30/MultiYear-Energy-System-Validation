"""Hourly resource access benchmark; no BA CF admission."""
import argparse,json,time,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from paper_a1_e4_weather_probe import STORE,VARIABLES
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    reports=[]
    for y in (2024,2025):
        for lat,lon in [(35,248),(32,260)]:
            start=time.monotonic()
            times=pd.date_range(f"{y}-07-01",periods=168,freq="h")
            v=ds[VARIABLES].sel(time=times.values).sel(latitude=lat,longitude=lon)
            f=v.to_dataframe().reset_index()
            if len(f)!=168 or not np.array_equal(f.time.values,times.values):raise ValueError("hourly clock mismatch")
            if not np.isfinite(f[VARIABLES].to_numpy()).all():raise ValueError("missing resource data")
            f["wind_speed_100m"]=np.hypot(f[VARIABLES[0]],f[VARIABLES[1]])
            f["radiation_j_m2"]=f[VARIABLES[3]]
            path=d/f"weather_{y}_{lat}_{lon}.csv";f.to_csv(path,index=False)
            reports.append(dict(year=y,lat=lat,lon=lon,hours=len(f),seconds=time.monotonic()-start,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),radiation_min=float(f.radiation_j_m2.min()),radiation_max=float(f.radiation_j_m2.max()),daily_radiation_mj_m2=(f.groupby(f.time.dt.date).radiation_j_m2.sum()/1e6).tolist(),wind_mean=float(f.wind_speed_100m.mean()),source_chunks={k:str(ds[k].encoding.get("chunks")) for k in VARIABLES}))
    (d/"benchmark.json").write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
if __name__=="__main__":main()
