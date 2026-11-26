"""Exact-key wind parameter audit, preserving official raw values and provenance."""
import hashlib,io,json,urllib.request,zipfile
from pathlib import Path
import pandas as pd
import openpyxl
from paper_a1_e4_wind_schema import SOURCES
FIELDS={"Plant Code":"plant","Generator ID":"gen","Status":"status","Nameplate Capacity (MW)":"official_mw","Number of Turbines":"count","Predominant Turbine Manufacturer":"manufacturer","Predominant Turbine Model Number":"model","Design Wind Speed (mph)":"design_mph","Wind Quality Class":"quality_class","Turbine Hub Height (Feet)":"hub_ft"}
def main():
    rows=[]
    for year,(url,sha) in SOURCES.items():
        with urllib.request.urlopen(url,timeout=180) as r:data=r.read()
        if hashlib.sha256(data).hexdigest()!=sha:raise ValueError("source changed")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name=next(n for n in z.namelist() if n.endswith(f"3_2_Wind_Y{year}.xlsx"))
            wb=openpyxl.load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
            s=wb["Operable"]; it=s.iter_rows(values_only=True);next(it);header=list(next(it))
            for i,row in enumerate(it,3):
                if row[header.index("Plant Code")] is None:continue
                v={k:row[header.index(h)] for h,k in FIELDS.items()}
                v.update(yr=year,workbook=name,sheet=s.title,excel_row=i,sha256=sha)
                rows.append(v)
            wb.close()
    o=pd.DataFrame(rows);o["plant"]=pd.to_numeric(o.plant,errors="raise").astype(int);o["gen"]=o.gen.astype(str).str.strip()
    o=o[o.status.astype(str).str.strip().eq("OP")].copy()
    keys=["yr","plant","gen"]
    if o.duplicated(keys).any():raise ValueError("duplicate official key")
    w=pd.read_csv("inputs/weights/renewable_plant_coordinates.csv",dtype={"gen":str})
    w=w[w.tech.str.contains("Wind Turbine")].copy();w.gen=w.gen.str.strip()
    a=w.merge(o,on=keys,how="left",validate="one_to_one",indicator=True)
    a["matched"]=a["_merge"].eq("both")
    for k in ["official_mw","count","hub_ft","design_mph"]:a[k+"_numeric"]=pd.to_numeric(a[k],errors="coerce")
    a["hub_m"]=a.hub_ft_numeric*.3048
    a["mw_per_turbine"]=a.official_mw_numeric/a.count_numeric.where(a.count_numeric.gt(0))
    a["mw_agree"]=(a.mw-a.official_mw_numeric).abs().le(.01)
    a["model_present"]=a.manufacturer.fillna("").astype(str).str.strip().ne("") & a.model.fillna("").astype(str).str.strip().ne("")
    a["hub_positive"]=a.hub_m.gt(0)
    a["count_positive"]=a.count_numeric.gt(0)&a.count_numeric.mod(1).eq(0)
    d=Path("results/wind_parameters");d.mkdir(parents=True,exist_ok=True)
    o.to_csv(d/"official_op.csv",index=False);a.to_csv(d/"exact_key_audit.csv",index=False)
    reports=[]
    for (y,ba),g in a.groupby(["yr","ba"]):
        r=dict(year=int(y),ba=ba,records=len(g),mw=float(g.mw.sum()))
        for k in ["matched","mw_agree","model_present","hub_positive","count_positive"]:
            r[k+"_records"]=int(g[k].sum());r[k+"_mw"]=float(g.loc[g[k],"mw"].sum())
        reports.append(r)
    (d/"coverage.json").write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
if __name__=="__main__":main()
