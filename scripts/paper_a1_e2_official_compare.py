"""Compare exact source keys across annual EIA worksheets, not physical identity."""
import argparse,csv,json
from collections import defaultdict,Counter
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    def read(name):
        with (d/name).open(newline="") as f:
            return list(csv.DictReader(f))
    packet=read("e2_b2_first_review_packet.csv")
    rows=read("e2_b2_official_generator_rows.csv")
    index=defaultdict(list)
    for r in rows:
        index[(r["year"],r["plant_id_eia"],r["generator_id"])].append(r)
    def describe(r):
        fields=json.loads(r["raw_fields_json"])
        selected={k:v for k,v in fields.items() if any(t in k.lower() for t in ("status","nameplate","operating year","operating month","retirement","prime mover","energy source 1","technology"))}
        return {"sheet":r["worksheet"],"row":r["excel_row"],"workbook":r["workbook"],"fields":selected}
    output=[]
    for r in packet:
        y=r["report_year"]
        other=r["year_b"] if y==r["year_a"] else r["year_a"]
        plant,gen=r["plant_id_eia"],r["generator_id"]
        a=index[(y,plant,gen)]
        b=index[(other,plant,gen)]
        if not a:
            raise ValueError("Frozen sample source key missing")
        result={"packet_rank":r["packet_rank"],"plant_id_eia":plant,"generator_id":gen,
            "source_year":y,"other_year":other,"source_rows":len(a),"other_year_exact_rows":len(b),
            "source_evidence":[describe(x) for x in a],"other_year_evidence":[describe(x) for x in b],
            "finding":"exact_key_present_in_both_official_vintages" if b else "exact_key_not_located_in_other_extracted_vintage",
            "physical_lineage_status":"unresolved"}
        output.append(result)
        print(json.dumps(result,ensure_ascii=True))
    summary={"sample_count":len(output),"findings":dict(Counter(x["finding"] for x in output)),
        "physical_links_verified":0,"records":output,
        "limitation":"Absence is limited to extracted generator worksheets; presence is not proof of physical identity."}
    (d/"e2_b2_official_exact_key_comparison.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary["findings"]))
if __name__=="__main__":
    main()
