"""Exploratory PV conversion; interval-average GHI at midpoint geometry.
No empirical calibration or formal resource admission.
"""
import numpy as np
import pandas as pd
import pvlib

def pv_cf(time,lat,lon,ghi,temp_c,mount,dc_ac,tilt=None,azimuth=None):
    t=pd.DatetimeIndex(time)
    g=np.asarray(ghi,float);temp=np.asarray(temp_c,float)
    if t.tz is None or len(t)!=len(g) or g.shape!=temp.shape or not np.isfinite(g).all() or not np.isfinite(temp).all() or (g<0).any() or not .5<=dc_ac<=3:raise ValueError("invalid PV inputs")
    pos=pvlib.solarposition.get_solarposition(t,lat,lon)
    zen=pos.apparent_zenith.to_numpy();az=pos.azimuth.to_numpy()
    day=zen<90
    er=pvlib.irradiance.erbs(g,zen,t)
    dni=np.where(day,np.asarray(er["dni"]),0);dhi=np.where(day,np.asarray(er["dhi"]),0)
    def plane(beta,gamma):
        poa=pvlib.irradiance.get_total_irradiance(beta,gamma,zen,az,dni,g,dhi,albedo=.2)["poa_global"]
        return np.where(day,np.nan_to_num(poa,nan=0),0).clip(0)
    if mount=="single":
        tr=pvlib.tracking.singleaxis(zen,az,axis_tilt=0,axis_azimuth=0,max_angle=60,backtrack=True,gcr=.35)
        poa=plane(tr["surface_tilt"],tr["surface_azimuth"])
    elif mount=="dual":poa=plane(zen,az)
    elif mount in ("fixed","eastwest"):
        if tilt is None or not 0<=tilt<=90:raise ValueError("fixed tilt required")
        if mount=="eastwest":poa=(plane(tilt,90)+plane(tilt,270))/2
        else:
            if azimuth is None or not 0<=azimuth<=360:raise ValueError("fixed azimuth required")
            poa=plane(tilt,azimuth)
    else:raise ValueError("unresolved mount")
    cell=temp+.03*poa
    dc=dc_ac*poa/1000*np.maximum(0,1-.004*(cell-25))
    return np.clip(.96*dc,0,1)

def self_test():
    t=pd.date_range("2025-06-21",periods=24,freq="h",tz="UTC")
    pos=pvlib.solarposition.get_solarposition(t,35,-106)
    g=np.maximum(0,np.cos(np.deg2rad(pos.apparent_zenith)))*900
    for m in ("single","dual","fixed","eastwest"):
        cf=pv_cf(t,35,-106,g,np.full(24,25.),m,1.3,30,180)
        assert np.isfinite(cf).all() and ((cf>=0)&(cf<=1)).all() and cf.max()>0
        assert (cf[pos.apparent_zenith>=90]==0).all()
        print(m,float(cf.sum()),float(cf.max()))
    print("pv_kernel_tests_passed")
if __name__=="__main__":self_test()
