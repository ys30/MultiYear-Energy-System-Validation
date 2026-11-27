"""Screen representative curves by unit rating; no generation-based tuning."""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import atlite,yaml
def main():
    root=Path(atlite.__file__).parent/"resources"/"windturbine"
    catalog=[]
    for p in sorted(root.glob("*.yaml")):
        if "offshore" in p.stem.lower():continue
        raw=yaml.safe_load(p.read_text())
        v=np.asarray(raw["V"],float); power=np.asarray(raw["POW"],float)
        if len(v)!=len(power) or len(v)<2 or not np.isfinite(v).all() or not np.isfinite(power).all() or not (np.diff(v)>=0).all() or (power<0).any() or power.max()<=0:continue
        # atlite turbine YAML POW is MW; explicitly screen plausible ratings.
        rating=float(power.max())
        if not .05<=rating<=20:continue
        catalog.append(dict(curve=p.stem,rating_mw=rating,hub_m=raw.get("HUB_HEIGHT"),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),speed=v.tolist(),power_mw=power.tolist(),duplicate_nodes=int((np.diff(v)==0).sum())))
    if not catalog:raise ValueError("no screened curves")
    a=pd.read_csv("inputs/wind/exact_key_audit.csv",dtype={"gen":str})
    rows=[]
    for r in a.itertuples(index=False):
        unit=r.mw_per_turbine
        valid=bool(all(pd.notna(x) and str(x).lower()=="true" for x in (r.matched,r.mw_agree,r.count_positive)) and np.isfinite(unit) and .05<=unit<=20 and 20<=r.hub_m<=200)
        best=None
        if valid:
            best=min(catalog,key=lambda c:(abs(np.log(c["rating_mw"]/unit)),c["curve"]))
        ratio=best["rating_mw"]/unit if best else None
        rows.append(dict(yr=r.yr,plant=r.plant,gen=r.gen,ba=r.ba,mw=r.mw,unit_mw=unit,hub_m=r.hub_m,curve=best["curve"] if best else None,curve_sha256=best["sha256"] if best else None,rating_ratio=ratio,within_25pct=bool(best and .8<=ratio<=1.25),admitted=False))
    d=Path("results/representative");d.mkdir(parents=True,exist_ok=True)
    b=pd.DataFrame(rows);b.to_csv(d/"assignments.csv",index=False)
    (d/"catalog.json").write_text(json.dumps(catalog,indent=2))
    report=[]
    for (y,ba),g in b.groupby(["yr","ba"]):
        report.append(dict(year=int(y),ba=ba,mw=float(g.mw.sum()),candidate_mw=float(g.loc[g.curve.notna(),"mw"].sum()),within_25pct_mw=float(g.loc[g.within_25pct,"mw"].sum())))
    (d/"coverage.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(curves=len(catalog),coverage=report,admitted=False)))
if __name__=="__main__":main()
