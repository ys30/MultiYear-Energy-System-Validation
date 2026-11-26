"""Inspect pinned official EIA860 storage workbooks and preserve energy rating field evidence."""
import argparse,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
from openpyxl import load_workbook
from paper_a1_e2_official_archive_audit import ARCHIVES
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    result=[]
    for y,(url,sha) in ARCHIVES.items():
        with urllib.request.urlopen(url,timeout=120) as f:raw=f.read()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("archive changed")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for name in z.namelist():
                if "storage" not in name.lower() or not name.lower().endswith(".xlsx"):continue
                wb=load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
                for ws in wb:
                    rows=[]
                    for i,row in enumerate(ws.iter_rows(values_only=True),1):
                        if i>8:break
                        rows.append([str(v) if v is not None else None for v in row])
                    result.append(dict(year=y,workbook=name,sheet=ws.title,header_rows=rows,archive_sha256=sha))
                wb.close()
    (d/"storage_schema.json").write_text(json.dumps(result,indent=2));print(json.dumps(result))
    if set(r["year"] for r in result)!=set(ARCHIVES):raise ValueError("storage workbook absent for one or more years")
if __name__=="__main__":main()
