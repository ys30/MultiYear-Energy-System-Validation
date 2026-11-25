"""Retrieve observed EIA-930 fuel generation and net interchange; never infer availability."""
import os,json,time,urllib.request,urllib.parse,argparse
from pathlib import Path
import pandas as pd
import numpy as np
BAS=("CISO","ERCO","AZPS","PNM","PSCO","IPCO","PACW")
def fetch(endpoint,year,ba,facet):
    params=[("api_key",os.environ["EIA_API_KEY"]),("frequency","hourly"),("data[0]","value"),("facets[respondent][]",ba),("start",f"{year}-01-01T00"),("end",f"{year}-12-31T23"),("length","5000"),("sort[0][column]","period"),("sort[0][direction]","asc"),("sort[1][column]",facet),("sort[1][direction]","asc")]
    if facet=="type":params.append(("facets[type][]","TI"))
    else:params.extend(("facets[fueltype][]",x) for x in ("SUN","WND"))
    rows=[];total=None
    while total is None or len(rows)<total:
        url="https://api.eia.gov/v2/electricity/rto/"+endpoint+"/data/?"+urllib.parse.urlencode(params+[("offset",str(len(rows)))])
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url,timeout=60) as f:r=json.load(f)["response"]
                break
            except Exception:
                if attempt==3:raise
                time.sleep(2**attempt)
        count=int(r["total"])
        if total is not None and total!=count:raise ValueError("unstable total")
        total=count
        if not r["data"]:break
        rows.extend(r["data"])
    if len(rows)!=total or not rows:raise ValueError("incomplete retrieval")
    x=pd.DataFrame(rows)[["period","respondent",facet,"value"]]
    x["period"]=pd.to_datetime(x.period,utc=True)
    x["value"]=pd.to_numeric(x.value,errors="coerce")
    expected=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    if x.duplicated(["period","respondent",facet]).any() or not x.period.isin(expected).all() or not x.respondent.eq(ba).all():raise ValueError("invalid keys")
    return x,expected
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--year",type=int,required=True);p.add_argument("--ba",required=True,choices=BAS);a=p.parse_args()
    d=a.output_dir;d.mkdir(parents=True,exist_ok=True)
    report=[]
    for endpoint,facet,types in [("fuel-type-data","fueltype",("SUN","WND")),("region-data","type",("TI",))]:
        try:
            x,expected=fetch(endpoint,a.year,a.ba,facet)
            x.to_csv(d/f"{endpoint}_{a.ba}_{a.year}.csv",index=False)
            for t in types:
                v=x[x[facet].eq(t)]
                report.append(dict(year=a.year,ba=a.ba,series=t,rows=len(v),missing_hours=len(expected)-len(v),nonfinite=int((~np.isfinite(v.value)).sum()),negative=int(v.value.lt(0).sum()),observed_mwh=float(v.value.sum(min_count=1)) if v.value.notna().any() else None,status="retrieved" if len(v) else "absent"))
        except Exception as e:report.append(dict(year=a.year,ba=a.ba,endpoint=endpoint,status="blocked",error_type=type(e).__name__))
    (d/"manifest.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=="__main__":main()
