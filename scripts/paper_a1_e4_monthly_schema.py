"""D1 source discovery: inspect official July EIA-860M archives without inferring identities."""
import hashlib,io,json,zipfile
from pathlib import Path
import urllib.request
import pandas as pd
d=Path("results/monthly_schema");d.mkdir(parents=True,exist_ok=True)
results=[]
for year in (2024,2025):
    url=f"https://www.eia.gov/electricity/data/eia860m/archive/xls/july_generator{year}.xlsx"
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=120) as r: raw=r.read();final_url=r.geturl()
    if not zipfile.is_zipfile(io.BytesIO(raw)):raise ValueError("not an xlsx archive")
    book=pd.ExcelFile(io.BytesIO(raw),engine="openpyxl")
    sheets=[]
    for sheet in book.sheet_names:
        f=pd.read_excel(book,sheet_name=sheet,header=None,nrows=12,dtype=str).fillna("")
        sheets.append(dict(sheet=sheet,preview=f.values.tolist()))
    results.append(dict(year=year,month=7,url=url,final_url=final_url,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sheets=sheets))
    (d/f"july_{year}.xlsx").write_bytes(raw)
(d/"schema.json").write_text(json.dumps(results,indent=2));print(json.dumps(results))
