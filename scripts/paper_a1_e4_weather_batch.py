"""Seven-day all-grid resource extraction benchmark; preserve raw radiation."""
import argparse,json,time,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from paper_a1_e4_weather_probe import STORE,VARIABLES
def main():
    p=argparse.ArgumentParser();p.add_argument("--weights",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--year",type=int,required=True);a=p.parse_args();d=a.output_dir;d.mkdir(parents=True,exist_ok=True)
    w=pd.read_csv(a.weights);w=w[w.yr==a.year]
    cells=w[["grid_lat","grid_lon"]].drop_duplicates().sort_values(["grid_lat","grid_lon"]).reset_index(drop=True)
    if cells.empty:raise ValueError("no grid cells")
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    times=pd.date_range(f"{a.year}-07-01",periods=168,freq="h")
    lat=xr.DataArray(cells.grid_lat.values,dims="cell");lon=xr.DataArray(cells.grid_lon.values,dims="cell")
    start=time.monotonic();parts=[]
    for t in times:
        v=ds[VARIABLES].sel(time=t.to_datetime64()).sel(latitude=lat,longitude=lon)
        f=v.to_dataframe().reset_index()
        if len(f)!=len(cells) or not np.isfinite(f[VARIABLES].to_numpy()).all():raise ValueError("invalid grid hour")
        parts.append(f)
    f=pd.concat(parts,ignore_index=True)
    if len(f)!=168*len(cells) or f.duplicated(["time","latitude","longitude"]).any():raise ValueError("grid-hour mismatch")
    path=d/"raw_weather.csv";f.to_csv(path,index=False)
    r=dict(year=a.year,cells=len(cells),hours=168,rows=len(f),seconds=time.monotonic()-start,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),radiation_min=float(f[VARIABLES[3]].min()),radiation_max=float(f[VARIABLES[3]].max()),negative_radiation=int((f[VARIABLES[3]]<0).sum()),admitted_cf=False)
    (d/"batch_manifest.json").write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=="__main__":main()
