"""Print manuscript-ready E1.3 descriptive capacity summary from verified outputs."""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def summarize(rows):
    totals = defaultdict(lambda: {"records": 0, "with_capacity": 0, "mw": 0.0, "negative": 0})
    tech = defaultdict(lambda: {"records": 0, "mw": 0.0})
    for r in rows:
        key=(r["year_a"],r["year_b"],r["side"],r["plant_context"])
        totals[key]["records"]+=r["records"]
        totals[key]["with_capacity"]+=r["records_with_capacity"]
        totals[key]["mw"]+=r["sum_nonnegative_mw"] or 0.0
        totals[key]["negative"]+=r["negative_capacity_records"]
        t=(r["year_a"],r["year_b"],r["side"],r["technology"])
        tech[t]["records"]+=r["records"]
        tech[t]["mw"]+=r["sum_nonnegative_mw"] or 0.0
    by_context=[{"year_a":k[0],"year_b":k[1],"side":k[2],"plant_context":k[3],**v}
                for k,v in sorted(totals.items())]
    by_technology=[{"year_a":k[0],"year_b":k[1],"side":k[2],"technology":k[3],**v}
                   for k,v in sorted(tech.items())]
    return {"by_context":by_context,"by_technology":by_technology,
            "interpretation":"Reported MW on unmatched annual snapshots; not net additions or retirements"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    data=json.loads((folder/"unmatched_capacity_by_technology.json").read_text())
    out={"source_url":data["source_url"],**summarize(data["rows"])}
    (folder/"unmatched_capacity_summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E1.3 MW BY PLANT CONTEXT")
    print(json.dumps(out["by_context"],indent=2))
    print("E1.3 TOP TECHNOLOGIES BY REPORTED MW (per year and side)")
    for a,b in ((2023,2024),(2024,2025)):
        for side in ("only_in_earlier_year","only_in_later_year"):
            top=sorted((r for r in out["by_technology"] if r["year_a"]==a and r["year_b"]==b and r["side"]==side),
                       key=lambda r:r["mw"],reverse=True)[:5]
            print(json.dumps({"year_a":a,"year_b":b,"side":side,"top5":top}))


if __name__=="__main__":
    main()
