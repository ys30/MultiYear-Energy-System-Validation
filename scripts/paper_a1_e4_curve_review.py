"""Rank candidate names for review only; no automatic curve assignment."""
import json,re,difflib
from pathlib import Path
import pandas as pd
def norm(s):return re.sub(r"[^a-z0-9]","",str(s).lower())
def main():
    p=Path("inputs/inventory")
    a=pd.read_csv(p/"model_inventory.csv")
    c=json.loads((p/"catalog.json").read_text())["curves"]
    rows=[]
    for r in a.itertuples(index=False):
        keys=[norm(r.model),norm(str(r.manufacturer)+str(r.model))]
        scores=sorted([(max(difflib.SequenceMatcher(None,k,norm(x["name"])).ratio() for k in keys),x["name"],x["sha256"]) for x in c],reverse=True)
        for rank,(score,name,sha) in enumerate(scores[:3],1):
            rows.append(dict(manufacturer=r.manufacturer,model=r.model,records=r.records,mw=r.mw,rank=rank,curve=name,curve_sha256=sha,name_similarity=score,decision="unreviewed"))
    d=Path("results/curve_review");d.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).sort_values(["mw","rank"],ascending=[False,True]).to_csv(d/"review_queue.csv",index=False)
    print(json.dumps(dict(models=len(a),review_rows=len(rows),admitted=0,top_models=a.sort_values("mw",ascending=False).head(15)[["manufacturer","model","mw"]].to_dict("records"),catalog=[x["name"] for x in c])))
if __name__=="__main__":main()
