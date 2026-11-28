"""Predeclared generic turbine curve sensitivity, not fitted or admitted."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",type=Path,required=True);p.add_argument("--weights",type=Path,required=True);p.add_argument("--year",type=int,required=True);p.add_argument("--output-dir",type=Path,required=True);a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    f=pd.read_csv(a.raw);w=pd.read_csv(a.weights);w=w[(w.yr==a.year)&w.tech.eq("Onshore Wind Turbine")]
    j=f.merge(w,left_on=["latitude","longitude"],right_on=["grid_lat","grid_lon"])
    speed=np.hypot(j["100m_u_component_of_wind"],j["100m_v_component_of_wind"])
    rows=[];out=[]
    for rated in (8,9,10,11,12):
        for multiplier in (1.,1.15,1.30):
            v=speed*multiplier
            j["weighted"]=j.weight*np.where((v<3)|(v>=25),0,np.clip((v**3-27)/(rated**3-27),0,1))
            g=j.groupby(["time","ba"],as_index=False).agg(cf=("weighted","sum"),weight_sum=("weight","sum"))
            if len(g)!=168*7 or not np.allclose(g.weight_sum,1):raise ValueError("incomplete wind grid")
            g["rated"]=rated;g["speed_multiplier"]=multiplier;out.append(g)
            for ba,h in g.groupby("ba"):rows.append(dict(year=a.year,ba=ba,rated=rated,speed_multiplier=multiplier,mean_cf=float(h.cf.mean())))
    pd.concat(out).to_csv(a.output_dir/"wind_sensitivity.csv",index=False)
    (a.output_dir/"manifest.json").write_text(json.dumps(dict(admitted=False,fitted=False,rows=rows),indent=2));print(json.dumps(rows))
if __name__=="__main__":main()
