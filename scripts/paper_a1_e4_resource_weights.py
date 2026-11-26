"""Freeze later-year OP renewable fleet spatial weights, common to all scenarios."""
import argparse,json
from pathlib import Path
import duckdb
import pandas as pd
from paper_a1_capacity_breakdown import URL
BAS=["AZPS","CISO","ERCO","IPCO","PACW","PNM","PSCO"]
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    con=duckdb.connect()
    schema=con.execute(f"DESCRIBE SELECT * FROM read_parquet('{URL}')").df()
    (d/"schema.json").write_text(schema.to_json(orient="records"))
    q=con.execute(f"""SELECT year(report_date) yr,plant_id_eia plant,generator_id gen,balancing_authority_code_eia ba,technology_description tech,capacity_mw mw,latitude lat,longitude lon FROM read_parquet('{URL}') WHERE year(report_date) IN (2024,2025) AND operational_status_code='OP' AND technology_description IN ('Solar Photovoltaic','Onshore Wind Turbine','Offshore Wind Turbine')""").df()
    q=q[q.ba.isin(BAS)].copy()
    if q.duplicated(["yr","plant","gen"]).any():raise ValueError("duplicate renewable key")
    q["valid"]=q.lat.between(18,72)&q.lon.between(-180,-60)&q.mw.gt(0)
    q.to_csv(d/"renewable_plant_coordinates.csv",index=False)
    a=q[q.valid].copy();a["grid_lat"]=(a.lat*4).round()/4;a["grid_lon"]=((a.lon*4).round()/4)%360
    g=a.groupby(["yr","ba","tech","grid_lat","grid_lon"],as_index=False).mw.sum()
    g["weight"]=g.mw/g.groupby(["yr","ba","tech"]).mw.transform("sum")
    g.to_csv(d/"resource_grid_weights.csv",index=False)
    rows=[]
    for (y,ba,t),v in q.groupby(["yr","ba","tech"]):
        w=g[(g.yr==y)&(g.ba==ba)&(g.tech==t)]
        total=float(v.mw.sum());valid=float(v.loc[v.valid,"mw"].sum())
        rows.append(dict(year=int(y),ba=ba,technology=t,records=len(v),total_mw=total,valid_mw=valid,coverage=valid/total if total>0 else None,cells=len(w),weight_sum=float(w.weight.sum())))
    (d/"resource_weight_coverage.json").write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
if __name__=="__main__":main()
