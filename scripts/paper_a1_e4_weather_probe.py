"""Public ERA5 resource-variable access pilot; not BA capacity factors."""
import argparse,json
from pathlib import Path
import numpy as np
import xarray as xr
STORE="gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
VARIABLES=["100m_u_component_of_wind","100m_v_component_of_wind","2m_temperature","surface_solar_radiation_downwards"]
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    meta={v:dict(dims=list(ds[v].dims),attrs=dict(ds[v].attrs),shape=list(ds[v].shape)) for v in VARIABLES if v in ds}
    (d/"metadata.json").write_text(json.dumps(dict(store=STORE,variables=meta,available=list(ds.data_vars)),default=str,indent=2))
    if set(meta)!=set(VARIABLES):raise ValueError("resource variable absent")
    rows=[]
    for year in (2024,2025):
        for lat,lon in [(35,-112),(32,-100)]:
            for hour in (0,12,18):
                stamp=np.datetime64(f"{year}-07-01T{hour:02}:00:00")
                v=ds[VARIABLES].sel(time=stamp).sel(latitude=lat,longitude=lon%360,method="nearest")
                r=dict(year=year,time=str(v.time.values),lat=float(v.latitude),lon=float(v.longitude))
                for k in VARIABLES:r[k]=float(v[k].values)
                if not all(np.isfinite(r[k]) for k in VARIABLES):raise ValueError("nonfinite resource sample")
                r["wind_speed_100m"]=float(np.hypot(r[VARIABLES[0]],r[VARIABLES[1]]))
                rows.append(r)
    (d/"samples.json").write_text(json.dumps(rows,indent=2));print(json.dumps(dict(metadata=meta,samples=rows),default=str))
if __name__=="__main__":main()
