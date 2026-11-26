"""Compare archived API observations with bulk candidates; admit only uniquely supported clock."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
def main():
    p=argparse.ArgumentParser();p.add_argument("--bulk",type=Path,required=True);p.add_argument("--api",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    b=pd.read_csv(a.bulk,low_memory=False)
    for c in ("utc_start","utc_end"):b[c]=pd.to_datetime(b[c],utc=True)
    reports=[];outputs=[]
    for path in sorted(a.api.rglob("*.csv")):
        if not path.name.startswith(("fuel-type-data_","region-data_")):continue
        x=pd.read_csv(path);facet="fueltype" if "fueltype" in x else "type"
        x["period"]=pd.to_datetime(x.period,utc=True)
        for (ba,t),v in x.groupby(["respondent",facet]):
            col={"SUN":"Solar_candidate","WND":"Wind_candidate","TI":"Total Interchange (MW)"}.get(t)
            if col is None:continue
            year=int(v.period.dt.year.iloc[0]);grid=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
            api=v.set_index("period").value.reindex(grid)
            q=b[b["Balancing Authority"].eq(ba)]
            scores=[];candidates={}
            for clock in ("utc_end","utc_start"):
                bulk=q.set_index(clock)[col].reindex(grid);both=api.notna()&bulk.notna()
                equal=int(np.isclose(api[both],bulk[both],atol=0.01,rtol=0).sum())
                scores.append(dict(clock=clock,overlap=int(both.sum()),equal=equal,rate=equal/max(1,int(both.sum()))));candidates[clock]=bulk
            scores.sort(key=lambda r:r["rate"],reverse=True)
            best=scores[0];admitted=best["overlap"]>=1000 and best["rate"]>=.95 and best["rate"]-scores[1]["rate"]>=.05
            bulk=candidates[best["clock"]];fill=api.isna()&bulk.notna() if admitted else pd.Series(False,index=grid)
            # Split fuel components are candidates only; do not admit until semantic audit.
            if t in ("SUN","WND"):fill[:]=False
            out=pd.DataFrame(dict(period=grid,ba=ba,series=t,api=api.values,bulk_candidate=bulk.values,selected=api.where(~fill,bulk).values,source=np.where(api.notna(),"api",np.where(fill,"bulk_raw","missing"))))
            outputs.append(out)
            reports.append(dict(year=year,ba=ba,series=t,scores=scores,clock_admitted=admitted,api_missing=int(api.isna().sum()),candidate_recoverable=int((api.isna()&bulk.notna()).sum()),admitted_recovered=int(fill.sum()),remaining=int(out.selected.isna().sum())))
    if len(reports)!=42:raise ValueError(f"expected 42 series, got {len(reports)}")
    pd.concat(outputs).to_csv(a.output_dir/"reconciled.csv",index=False)
    (a.output_dir/"reconciliation.json").write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
if __name__=="__main__":main()
