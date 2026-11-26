"""Extract seven BA cohorts from pinned bulk files; preserve component nulls and revisions."""
import argparse,hashlib,io,json,urllib.request
from pathlib import Path
import pandas as pd
FILES={(2024,"Jan_Jun"):"26768c495c3ba987e29d79df2e40d4e741f9dbcff086f53c12ff774465756a10",(2024,"Jul_Dec"):"a602a8e577cfdd2fa3083413eaa4dd8ba7f0d2b26a2986f8f6d22917465ea49f",(2025,"Jan_Jun"):"fac4bb991dfa1dab3b4b35300ccab54ac99be13a40ce91954db8ddafb2816242",(2025,"Jul_Dec"):"1146158b972439db7c7f4cc7d0491e07644ddbf244d03b8ecb44cb2c833d10f1"}
BAS=["CISO","ERCO","AZPS","PNM","PSCO","IPCO","PACW"]
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    frames=[]
    for (y,h),sha in FILES.items():
        url=f"https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{y}_{h}.csv"
        with urllib.request.urlopen(url,timeout=180) as f:raw=f.read()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("source changed")
        x=pd.read_csv(io.BytesIO(raw),low_memory=False);x=x[x["Balancing Authority"].isin(BAS)].copy()
        x["source_file"]=f"{y}_{h}";x["source_sha256"]=sha
        x["utc_end"]=pd.to_datetime(x["UTC Time at End of Hour"],format="%m/%d/%Y %I:%M:%S %p",utc=True)
        x["utc_start"]=x.utc_end-pd.Timedelta(hours=1)
        for suffix in (""," (Imputed)"," (Adjusted)"):
            for fuel in ("Solar","Wind"):
                base="Net Generation (MW) from "+fuel
                if base+suffix in x:
                    x[f"{fuel}{suffix}_candidate"]=pd.to_numeric(x[base+suffix],errors="raise")
                else:
                    cols=[base+" without Integrated Battery Storage"+suffix,base+" with Integrated Battery Storage"+suffix]
                    if fuel=="Solar" and suffix==" (Adjusted)":cols[1]=base+" witho Integrated Battery Storage"+suffix
                    v=x[cols].apply(pd.to_numeric,errors="raise")
                    x[f"{fuel}{suffix}_candidate"]=v.sum(axis=1,min_count=1)
                    x[f"{fuel}{suffix}_component_count"]=v.notna().sum(axis=1)
        frames.append(x)
    a=pd.concat(frames,ignore_index=True)
    if a.duplicated(["Balancing Authority","utc_end"]).any():raise ValueError("duplicate BA UTC end")
    a.to_csv(d/"bulk_selected_raw.csv",index=False)
    report=[]
    for y in (2024,2025):
        for ba in BAS:
            for clock in ("utc_end","utc_start"):
                t=a[a["Balancing Authority"].eq(ba)&a[clock].dt.year.eq(y)]
                r=dict(year=y,ba=ba,clock=clock,rows=len(t))
                for col in ["Demand (MW)","Total Interchange (MW)","Solar_candidate","Wind_candidate","Total Interchange (MW) (Adjusted)","Solar (Adjusted)_candidate","Wind (Adjusted)_candidate"]:
                    r[col+"_count"]=int(t[col].notna().sum())
                    r[col+"_sum"]=float(t[col].sum())
                report.append(r)
    (d/"bulk_coverage.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=="__main__":main()
