"""Inspect official solar workbook headers from pinned EIA860 archives."""
import hashlib,io,json,urllib.request,zipfile
from pathlib import Path
import openpyxl
from paper_a1_e4_wind_schema import SOURCES
def main():
    out=[]
    for year,(url,sha) in SOURCES.items():
        with urllib.request.urlopen(url,timeout=180) as r:data=r.read()
        if hashlib.sha256(data).hexdigest()!=sha:raise ValueError("source changed")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=[n for n in z.namelist() if "solar" in n.lower() and n.lower().endswith(".xlsx")]
            if not names:raise ValueError("solar workbook absent")
            for name in names:
                wb=openpyxl.load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
                for s in wb:
                    rows=list(s.iter_rows(min_row=1,max_row=5,values_only=True))
                    out.append(dict(year=year,workbook=name,sheet=s.title,rows=s.max_row,sha256=sha,first_rows=rows))
                wb.close()
    p=Path("results/solar_schema.json");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,default=str,indent=2));print(json.dumps(out,default=str))
if __name__=="__main__":main()
