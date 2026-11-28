"""Compute scope sensitivity from verified detailed status groups."""
import argparse,csv,json
from pathlib import Path
from collections import defaultdict

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    with (d/"unmatched_existing_by_status_code.csv").open(newline="") as f:
        rows=list(csv.DictReader(f))
    scopes={"OP_only":{"OP"},"OP_plus_SB":{"OP","SB"},"all_existing":{"OP","SB","OA","OS"}}
    if {r["operational_status_code"] for r in rows}!=scopes["all_existing"]:
        raise ValueError("Unexpected status code")
    result=[]
    for name,codes in scopes.items():
        groups=defaultdict(lambda: [0,0.0])
        for r in rows:
            if r["operational_status_code"] in codes:
                k=(r["year_a"],r["year_b"],r["side"])
                groups[k][0]+=int(r["records"])
                groups[k][1]+=float(r["sum_nonnegative_mw"])
        for (a,b,side),(n,mw) in sorted(groups.items()):
            result.append(dict(scope=name,year_a=a,year_b=b,side=side,records=n,reported_mw=round(mw,6)))
    for name,expected in [("OP_only",14451.9),("OP_plus_SB",14586.2),("all_existing",15095.9)]:
        if abs(sum(r["reported_mw"] for r in result if r["scope"]==name)-expected)>0.001:
            raise ValueError("Frozen scope total mismatch")
    with (d/"e3_status_scope_sensitivity.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]))
        w.writeheader()
        w.writerows(result)
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
