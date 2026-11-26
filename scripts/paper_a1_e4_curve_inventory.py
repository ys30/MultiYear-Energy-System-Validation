"""Inventory official turbine models and candidate atlite curves; no automatic admission."""
import json,re,importlib.metadata
from pathlib import Path
import pandas as pd
import atlite
def norm(s):return re.sub(r"[^a-z0-9]","",str(s).lower())
def main():
    d=Path("results/curve_inventory");d.mkdir(parents=True,exist_ok=True)
    a=pd.read_csv("inputs/wind/exact_key_audit.csv",dtype={"gen":str})
    root=Path(atlite.__file__).parent/"resources"/"windturbine"
    curves=sorted(root.glob("*.yaml"))
    if not curves:raise ValueError("no atlite turbine YAML files")
    import hashlib
    catalog=[dict(name=p.stem,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in curves]
    (d/"catalog.json").write_text(json.dumps(dict(version=importlib.metadata.version("atlite"),curves=catalog),indent=2))
    rows=[]
    for (manufacturer,model),g in a[a.matched].groupby(["manufacturer","model"],dropna=False):
        candidates=[p.stem for p in curves if norm(p.stem) in {norm(model),norm(str(manufacturer)+str(model))}]
        rows.append(dict(manufacturer=manufacturer,model=model,records=len(g),mw=float(g.mw.sum()),candidate_names=";".join(candidates),candidate_count=len(candidates)))
    pd.DataFrame(rows).to_csv(d/"model_inventory.csv",index=False)
    a["hub_range_screen"]=a.hub_m.between(20,200)
    a["unit_mw_screen"]=a.mw_per_turbine.between(.05,20)
    a.to_csv(d/"physical_screen.csv",index=False)
    print(json.dumps(dict(models=len(rows),curves=len(curves),candidate_records=sum(r["records"] for r in rows if r["candidate_count"]==1),candidate_mw=sum(r["mw"] for r in rows if r["candidate_count"]==1),total_mw=float(a.mw.sum()),admitted=False)))
if __name__=="__main__":main()
