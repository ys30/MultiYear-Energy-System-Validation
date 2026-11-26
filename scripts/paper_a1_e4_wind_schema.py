"""Inspect pinned official EIA860 wind workbook fields without assuming turbine specifications."""
import hashlib, io, json, urllib.request, zipfile
from pathlib import Path
import openpyxl
SOURCES={
2024:("https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip","0aaae04812cd4ab87a3e346bdf93848a3cc15053fd4dc2a4cf82d2aeac95f12b"),
2025:("https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip","2b27929d26cc1da9ad6a530da1cac6718cd8496098ee560c4d47cfffd96d08ba")}
def main():
    out=[]
    for year,(url,sha) in SOURCES.items():
        with urllib.request.urlopen(url,timeout=180) as r: data=r.read()
        if hashlib.sha256(data).hexdigest()!=sha:raise ValueError(f"source changed {year}")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=[n for n in z.namelist() if "wind" in n.lower() and n.lower().endswith(".xlsx")]
            if not names:raise ValueError("wind workbook absent")
            for name in names:
                wb=openpyxl.load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
                for sheet in wb:
                    rows=list(sheet.iter_rows(min_row=1,max_row=5,values_only=True))
                    out.append(dict(year=year,url=url,sha256=sha,workbook=name,sheet=sheet.title,rows=sheet.max_row,first_rows=rows))
                wb.close()
    p=Path("results/wind_schema.json");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,default=str,indent=2));print(json.dumps(out,default=str))
if __name__=="__main__":main()
