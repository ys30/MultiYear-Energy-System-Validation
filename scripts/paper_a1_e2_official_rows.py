"""Locate official generator workbook rows for sampled plants, preserving source coordinates."""
import argparse,csv,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
from openpyxl import load_workbook
from paper_a1_e2_official_archive_audit import ARCHIVES

def norm(v):
    return " ".join(str(v or "").strip().lower().split())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    folder=p.parse_args().output_dir
    with (folder/"e2_b2_first_review_packet.csv").open(newline="") as f:
        packet=list(csv.DictReader(f))
    plants={y:{int(r["plant_id_eia"]) for r in packet if y in (int(r["year_a"]),int(r["year_b"]))} for y in ARCHIVES}
    results=[]
    diagnostics=[]
    for year,(url,expected) in ARCHIVES.items():
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ResearchArchiveAudit/1.0"}),timeout=90) as response:
            raw=response.read()
        if hashlib.sha256(raw).hexdigest()!=expected:
            raise ValueError(f"Archive hash mismatch {year}")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names=[n for n in z.namelist() if "generator" in n.lower() and n.lower().endswith(".xlsx")]
            if not names:
                raise ValueError(f"No generator workbook {year}")
            for name in names:
                wb=load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
                for ws in wb:
                    header=None
                    count=0
                    for idx,row in enumerate(ws.iter_rows(values_only=True),1):
                        if header is None:
                            labels=[norm(v) for v in row]
                            if "plant code" in labels and "generator id" in labels:
                                header=labels
                                pi=labels.index("plant code")
                                gi=labels.index("generator id")
                            elif idx>=15:
                                break
                            continue
                        try:
                            plant=int(row[pi])
                        except (ValueError,TypeError):
                            continue
                        if plant not in plants[year] or row[gi] is None:
                            continue
                        fields={f"{i+1}:{header[i]}":v for i,v in enumerate(row) if i<len(header) and header[i] and v is not None}
                        results.append({"year":year,"plant_id_eia":plant,"generator_id":str(row[gi]).strip(),
                            "archive_url":url,"archive_sha256":expected,"workbook":name,
                            "worksheet":ws.title,"excel_row":idx,"raw_fields_json":json.dumps(fields,default=str)})
                        count+=1
                    diagnostics.append({"year":year,"workbook":name,"worksheet":ws.title,"header_found":header is not None,"rows":count})
                wb.close()
    if not results or any(not any(r["year"]==y for r in results) for y in ARCHIVES):
        raise ValueError("No extracted official rows for one or more years")
    keys={(r["year"],r["plant_id_eia"],r["generator_id"]) for r in results}
    hits=[]
    for r in packet:
        key=(int(r["report_year"]),int(r["plant_id_eia"]),r["generator_id"])
        hits.append({"packet_rank":r["packet_rank"],"source_key":list(key),"official_exact_key_found":key in keys})
    with (folder/"e2_b2_official_generator_rows.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)
    summary={"official_rows":len(results),"sample_exact_keys_found":sum(h["official_exact_key_found"] for h in hits),
        "sample_count":len(packet),"sample_checks":hits,"worksheet_diagnostics":diagnostics,
        "physical_links_verified":0}
    (folder/"e2_b2_official_rows_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
