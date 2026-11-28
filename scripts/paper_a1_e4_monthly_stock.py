"""D1 exact-key stock comparison; monthly snapshots are not hourly availability."""
import hashlib,json
from pathlib import Path
import pandas as pd
import numpy as np
d=Path("results/monthly_stock");d.mkdir(parents=True,exist_ok=True)
annual=pd.read_csv("inputs/weights/renewable_plant_coordinates.csv",dtype={"gen":str})
bas=["AZPS","CISO","ERCO","IPCO","PACW","PNM","PSCO"]
techs=["Onshore Wind Turbine","Solar Photovoltaic","Offshore Wind Turbine"]
keys=["plant","gen"]
hashes={2024:"983796eaa6c40b68ed32a6bea84477c5f31066384e276ad3bf794ccd70315693",2025:"6c004fd52982e94a9c0180af7076dd5633fab3fc90fa43ee580065c9a2a14056"}
rename={"Plant ID":"plant","Generator ID":"gen","Balancing Authority Code":"ba","Technology":"tech","Nameplate Capacity (MW)":"mw","Status":"status","Operating Month":"op_month","Operating Year":"op_year"}
rows=[];audits=[]
for y in (2024,2025):
    path=Path(f"inputs/monthly/july_{y}.xlsx")
    if hashlib.sha256(path.read_bytes()).hexdigest()!=hashes[y]:raise ValueError("source hash mismatch")
    m=pd.read_excel(path,sheet_name="Operating",header=2,dtype={"Generator ID":str}).rename(columns=rename)
    m=m[m.plant.notna() & m.gen.notna()].copy()
    m=m[m.status.fillna("").str.startswith("(OP)")].copy()
    m["plant"]=pd.to_numeric(m.plant,errors="raise").astype(int)
    m["mw"]=pd.to_numeric(m.mw,errors="raise")
    a=annual[annual.yr.eq(y)].copy()
    if a.duplicated(keys).any() or m.duplicated(keys).any():raise ValueError("duplicate generator key")
    if not np.isfinite(m.mw).all():raise ValueError("nonfinite monthly MW")
    j=a[keys+["ba","tech","mw"]].merge(m[keys+["ba","tech","mw","op_month","op_year"]],on=keys,how="outer",suffixes=("_annual","_monthly"),indicator=True,validate="one_to_one")
    j["year"]=y
    relevant=(j.ba_annual.isin(bas)&j.tech_annual.isin(techs))|(j.ba_monthly.isin(bas)&j.tech_monthly.isin(techs))
    audits.append(j[relevant])
    for ba in bas:
        for tech in techs[:2]:
            x=j.ba_annual.eq(ba)&j.tech_annual.eq(tech);z=j.ba_monthly.eq(ba)&j.tech_monthly.eq(tech)
            both=x&z
            am=j.loc[x,"mw_annual"].sum();mm=j.loc[z,"mw_monthly"].sum()
            rows.append(dict(year=y,ba=ba,tech=tech,annual_mw=am,july_mw=mm,delta_mw=am-mm,annual_only_scope_mw=j.loc[x&~z,"mw_annual"].sum(),monthly_only_scope_mw=j.loc[z&~x,"mw_monthly"].sum(),matched_delta_mw=(j.loc[both,"mw_annual"]-j.loc[both,"mw_monthly"]).sum(),matched_keys=int(both.sum()),annual_absent_monthly_mw=j.loc[x&j["_merge"].eq("left_only"),"mw_annual"].sum(),monthly_absent_annual_mw=j.loc[z&j["_merge"].eq("right_only"),"mw_monthly"].sum()))
s=pd.DataFrame(rows)
if not np.allclose(s.delta_mw,s.annual_only_scope_mw-s.monthly_only_scope_mw+s.matched_delta_mw):raise ValueError("stock reconciliation failed")
s.to_csv(d/"summary.csv",index=False);pd.concat(audits).to_csv(d/"exact_key_audit.csv",index=False);print(s.to_json(orient="records"))
