"""Audit monthly raw weather artifacts against exact UTC calendar and pinned grid weights."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from paper_a1_e4_weather_probe import VARIABLES

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--weights",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--require-full",action="store_true")
    a=p.parse_args()
    w=pd.read_csv(a.weights)
    seen=set(); reports=[]
    for manifest in sorted(a.root.rglob("batch_manifest.json")):
        m=json.loads(manifest.read_text()); y=int(m["year"]); month=int(m["month"])
        if y not in (2024,2025) or not 1<=month<=12 or (y,month) in seen:
            raise ValueError(f"invalid or duplicate month: {manifest}")
        first=pd.Timestamp(year=y,month=month,day=1,tz="UTC")
        times=pd.date_range(first,first+pd.offsets.MonthBegin(1),freq="h",inclusive="left")
        cells=w.loc[w.yr.eq(y),["grid_lat","grid_lon"]].drop_duplicates()
        expected=pd.MultiIndex.from_product([times,range(len(cells))])
        path=manifest.parent/"raw_weather.csv"
        if hashlib.sha256(path.read_bytes()).hexdigest()!=m["sha256"]:raise ValueError("hash mismatch")
        f=pd.read_csv(path)
        f["time"]=pd.to_datetime(f.time,utc=True)
        cells=cells.rename(columns={"grid_lat":"latitude","grid_lon":"longitude"}).reset_index(drop=True)
        cells["cell"]=cells.index
        f=f.merge(cells,on=["latitude","longitude"],how="left",validate="many_to_one")
        if f.cell.isna().any() or f.duplicated(["time","cell"]).any():raise ValueError("invalid grid keys")
        actual=pd.MultiIndex.from_frame(f[["time","cell"]])
        if len(actual)!=len(expected) or len(expected.difference(actual)) or len(actual.difference(expected)):raise ValueError("calendar or grid coverage mismatch")
        if not np.isfinite(f[VARIABLES].to_numpy()).all() or (f[VARIABLES[3]] < -1).any():raise ValueError("invalid weather values")
        if m["rows"]!=len(f) or m["hours"]!=len(times) or m["cells"]!=len(cells):raise ValueError("manifest count mismatch")
        seen.add((y,month));reports.append(dict(year=y,month=month,hours=len(times),cells=len(cells),rows=len(f),sha256=m["sha256"]))
    if not reports:raise ValueError("no complete months")
    missing=sorted(set((y,m) for y in (2024,2025) for m in range(1,13))-seen)
    result=dict(months=reports,missing_months=missing,complete=not missing,rows=sum(r["rows"] for r in reports),admitted_cf=False)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result))
    if a.require_full and missing:raise ValueError("annual coverage incomplete")
if __name__=="__main__":main()
