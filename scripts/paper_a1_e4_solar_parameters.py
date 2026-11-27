"""Exact-key solar parameter coverage audit, preserving missing and mixed technology."""
import hashlib,io,json,urllib.request,zipfile
from pathlib import Path
import pandas as pd
from paper_a1_e4_wind_schema import SOURCES
def main():
    rows=[]
    fields={"Plant Code":"plant","Generator ID":"gen","Status":"status","Nameplate Capacity (MW)":"official_mw","Single-Axis Tracking?":"single","Dual-Axis Tracking?":"dual","Fixed Tilt?":"fixed","East West Fixed Tilt?":"eastwest","Bifacial?":"bifacial","Azimuth Angle":"azimuth","Tilt Angle":"tilt","DC Net Capacity (MW)":"dc_mw"}
    for y,(url,sha) in SOURCES.items():
        with urllib.request.urlopen(url,timeout=180) as r:b=r.read()
        if hashlib.sha256(b).hexdigest()!=sha:raise ValueError("source changed")
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            name=next(n for n in z.namelist() if "solar" in n.lower() and n.lower().endswith(".xlsx"))
            f=pd.read_excel(io.BytesIO(z.read(name)),sheet_name="Operable",header=1,dtype={"Generator ID":str})
            f=f.loc[f.Status.eq("OP"),list(fields)].rename(columns=fields)
            f["yr"]=y;f["sha256"]=sha;f["workbook"]=name;f["excel_row"]=f.index+3
            rows.append(f)
    q=pd.concat(rows,ignore_index=True)
    a=pd.read_csv("inputs/weights/renewable_plant_coordinates.csv",dtype={"gen":str})
    a=a[a.tech.eq("Solar Photovoltaic")].copy()
    if a.empty:raise ValueError("solar fleet empty; inspect technology labels")
    a=a.merge(q,on=["yr","plant","gen"],how="left",validate="one_to_one",indicator=True)
    a["matched"]=a._merge.eq("both")
    for k in ("official_mw","dc_mw","azimuth","tilt"):a[k]=pd.to_numeric(a[k],errors="coerce")
    a["mw_agree"]=(a.mw-a.official_mw).abs().le(.01)
    a["dc_ac"]=a.dc_mw/a.mw
    a["dc_valid"]=a.dc_ac.between(.5,3)
    flags=a[["single","dual","fixed","eastwest"]].apply(lambda s:s.astype(str).str.strip().str.upper().eq("Y"))
    a["mount_count"]=flags.sum(axis=1)
    a["mount"]=flags.idxmax(axis=1).where(a.mount_count.eq(1),"unresolved_or_mixed")
    a["azimuth_valid"]=a.azimuth.between(0,360)
    a["tilt_valid"]=a.tilt.between(0,90)
    d=Path("results/solar_parameters");d.mkdir(parents=True,exist_ok=True);a.to_csv(d/"exact_key_audit.csv",index=False)
    out=[]
    for (y,ba),g in a.groupby(["yr","ba"]):
        row=dict(year=int(y),ba=ba,records=len(g),mw=float(g.mw.sum()))
        for k in ("matched","mw_agree","dc_valid","azimuth_valid","tilt_valid"):
            row[k+"_mw"]=float(g.loc[g.matched & g[k],"mw"].sum())
        row["mount_mw"]={str(k):float(v) for k,v in g.groupby("mount").mw.sum().items()}
        out.append(row)
    (d/"coverage.json").write_text(json.dumps(out,indent=2));print(json.dumps(out))
if __name__=="__main__":main()
