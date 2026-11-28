"""Exact-key annual storage rating audit, preserving missing values and provenance."""
import argparse,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
import pandas as pd
import duckdb
from openpyxl import load_workbook
from paper_a1_e2_official_archive_audit import ARCHIVES
from paper_a1_capacity_breakdown import URL
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    rows=[]
    fields={"Plant Code":"plant","Generator ID":"gen","Status":"status","Technology":"technology","Nameplate Capacity (MW)":"mw","Nameplate Energy Capacity (MWh)":"mwh","Maximum Charge Rate (MW)":"charge_mw","Maximum Discharge Rate (MW)":"discharge_mw"}
    for y,(url,sha) in ARCHIVES.items():
        with urllib.request.urlopen(url,timeout=120) as f:raw=f.read()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("archive changed")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            name=next(n for n in z.namelist() if "energy_storage" in n.lower() and n.lower().endswith(".xlsx"))
            wb=load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
            for ws in wb:
                it=ws.iter_rows(values_only=True);next(it);header=list(next(it))
                idx={k:header.index(k) for k in fields}
                for i,row in enumerate(it,3):
                    if row[idx["Plant Code"]] is None:continue
                    try:plant=int(row[idx["Plant Code"]])
                    except (ValueError,TypeError):continue
                    r={v:row[idx[k]] for k,v in fields.items()};r.update(year=y,plant=plant,gen=str(r["gen"]).strip(),sheet=ws.title,workbook=name,excel_row=i,sha256=sha);rows.append(r)
            wb.close()
    a=pd.DataFrame(rows)
    for c in ("mw","mwh","charge_mw","discharge_mw"):
        a[c+"_raw"]=a[c];a[c]=pd.to_numeric(a[c],errors="coerce")
    a.to_csv(d/"storage_official_all.csv",index=False)
    op=a[(a.sheet=="Operable")&(a.status=="OP")].copy()
    if op.duplicated(["year","plant","gen"]).any():raise ValueError("duplicate official OP key")
    con=duckdb.connect();con.register("official",op)
    q=con.execute(f"""SELECT coalesce(o.year,year(g.report_date)) yr,coalesce(o.plant,g.plant_id_eia) plant,coalesce(o.gen,g.generator_id) gen,g.balancing_authority_code_eia ba,g.technology_description pudl_technology,g.capacity_mw pudl_mw,o.* EXCLUDE(year,plant,gen)
    FROM official o FULL OUTER JOIN (SELECT * FROM read_parquet('{URL}') WHERE year(report_date) BETWEEN 2023 AND 2025 AND operational_status_code='OP' AND technology_description IN ('Batteries','Hydroelectric Pumped Storage')) g ON o.year=year(g.report_date) AND o.plant=g.plant_id_eia AND o.gen=g.generator_id""").df()
    q["rating_valid"]=(q.mwh>0)&(q.mw>0)&(q.charge_mw>0)&(q.discharge_mw>0)
    q["mw_agree"]=(q.mw-q.pudl_mw).abs()<=.01
    q["duration_h"]=q.mwh/q.mw.where(q.mw>0)
    q.to_csv(d/"storage_exact_key_audit.csv",index=False)
    report=[]
    for (y,ba,tech),v in q.groupby(["yr","ba","pudl_technology"],dropna=False):
        valid=v.rating_valid&v.mw_agree
        report.append(dict(year=int(y),ba=str(ba),technology=str(tech),records=len(v),pudl_mw=float(v.pudl_mw.sum()),matched=int(v.mw.notna().sum()),valid=int(valid.sum()),valid_mw=float(v.loc[valid,"pudl_mw"].sum()),valid_mwh=float(v.loc[valid,"mwh"].sum())))
    (d/"storage_coverage.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=="__main__":main()
