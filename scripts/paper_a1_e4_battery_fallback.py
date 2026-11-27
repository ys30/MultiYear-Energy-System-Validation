"""Exploratory battery fallback sensitivity; not observed ratings."""
import argparse,json
from pathlib import Path
import pandas as pd
import duckdb
from paper_a1_capacity_breakdown import URL
BAS=["AZPS","CISO","ERCO","IPCO","PACW","PNM","PSCO"]
def main():
    p=argparse.ArgumentParser();p.add_argument("--duration",type=float,required=True);p.add_argument("--audit",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    q=pd.read_csv(a.audit,dtype={"gen":str})
    q=q[q.pudl_technology.eq("Batteries")].copy()
    if q.duplicated(["yr","plant","gen"]).any():raise ValueError("duplicate battery key")
    keys=duckdb.connect().execute(f"SELECT year(report_date) yr,plant_id_eia plant,generator_id gen FROM read_parquet('{URL}') WHERE year(report_date) BETWEEN 2023 AND 2025").df()
    if keys.duplicated(["yr","plant","gen"]).any():raise ValueError("duplicate fleet key")
    keysets={y:set(zip(v.plant,v.gen)) for y,v in keys.groupby("yr")}
    q["key"]=list(zip(q.plant,q.gen))
    q["valid"]=q.rating_valid.eq(True)&q.mw_agree.eq(True)
    missing=~q.valid
    if not q.loc[missing,"pudl_mw"].gt(0).all():raise ValueError("invalid fallback power")
    q.loc[missing,"mwh"]=q.loc[missing,"pudl_mw"]*a.duration
    for m in ("charge_mw","discharge_mw"):q.loc[missing,m]=q.loc[missing,"pudl_mw"]
    q["imputed"]=missing
    q["valid"]=True
    out=[]
    for y in (2024,2025):
        for ba in BAS:
            old=q[(q.yr==y-1)&(q.ba==ba)];new=q[(q.yr==y)&(q.ba==ba)]
            lost=old[~old.key.isin(keysets[y])];added=new[~new.key.isin(keysets[y-1])]
            for metric in ("pudl_mw","mwh","charge_mw","discharge_mw"):
                def total(v):
                    if metric=="pudl_mw":return float(v[metric].sum())
                    if not v.valid.all():return None
                    return float(v[metric].sum())
                s0,s2,minus,plus=map(total,(old,new,lost,added))
                s1=None if any(x is None for x in (s0,minus,plus)) else s0-minus+plus
                if s1 is not None and s1 < -1e-6:raise ValueError("negative counterfactual")
                out.append(dict(year=y,ba=ba,metric=metric,S0=s0,S1=s1,S2=s2,unmatched_lost=minus,unmatched_added=plus,old_imputed=int(old.imputed.sum()),new_imputed=int(new.imputed.sum()),duration_assumption=a.duration))
    if len(out)!=56:raise ValueError("scenario count")
    pd.DataFrame(out).to_csv(a.output_dir/"battery_scenarios.csv",index=False)
    (a.output_dir/"battery_scenarios.json").write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=="__main__":main()
