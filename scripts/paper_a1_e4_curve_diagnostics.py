"""Diagnose every atlite curve rejection without changing admission rules."""
import json
from pathlib import Path
import numpy as np
import atlite,yaml
def main():
    rows=[]
    for p in sorted((Path(atlite.__file__).parent/"resources"/"windturbine").glob("*.yaml")):
        a=yaml.safe_load(p.read_text());v=np.asarray(a["V"],float);w=np.asarray(a["POW"],float)
        reasons=[]
        if len(v)!=len(w) or len(v)<2:reasons.append("length")
        if not np.isfinite(v).all() or not np.isfinite(w).all():reasons.append("nonfinite")
        if (np.diff(v)<=0).any():reasons.append("nonincreasing_speed")
        if (w<0).any():reasons.append("negative_power")
        if not .05<=w.max()<=20:reasons.append("rating_range")
        rows.append(dict(curve=p.stem,keys=list(a),n=len(v),power_max=float(w.max()),hub_height=a.get("HUB_HEIGHT"),duplicate_speed_pairs=int((np.diff(v)==0).sum()),descending_speed_pairs=int((np.diff(v)<0).sum()),offshore_name="offshore" in p.stem.lower(),reasons=reasons,duplicate_pairs=[dict(speed=float(v[i]),power_before=float(w[i]),power_after=float(w[i+1])) for i in range(min(len(v),len(w))-1) if v[i]==v[i+1]]))
    d=Path("results/curve_diagnostics");d.mkdir(parents=True,exist_ok=True);(d/"diagnostics.json").write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
if __name__=="__main__":main()
