"""Piecewise wind curve kernel with explicit right-continuous discontinuities."""
import numpy as np

def capacity_factor(speed, nodes, power):
    v=np.asarray(nodes,dtype=float); p=np.asarray(power,dtype=float); x=np.asarray(speed,dtype=float)
    if v.ndim!=1 or p.shape!=v.shape or len(v)<2 or not np.isfinite(v).all() or not np.isfinite(p).all() or (np.diff(v)<0).any() or (p<0).any() or p.max()<=0 or not np.isfinite(x).all() or (x<0).any():
        raise ValueError("invalid curve or speed")
    u,first,counts=np.unique(v,return_index=True,return_counts=True)
    if len(u)<2:raise ValueError("insufficient unique nodes")
    left=p[first];right=p[first+counts-1]
    i=np.clip(np.searchsorted(u,x,side="right")-1,0,len(u)-2)
    frac=(x-u[i])/(u[i+1]-u[i])
    y=right[i]+frac*(left[i+1]-right[i])
    y=np.where(x==u[-1],right[-1],y)
    y=np.where((x<u[0])|(x>u[-1]),0,y)
    return np.clip(y/p.max(),0,1)

def hub_speed(u100,v100,hub_m,alpha=1/7):
    u=np.asarray(u100,float);v=np.asarray(v100,float);h=np.asarray(hub_m,float)
    if not all(np.isfinite(a).all() for a in (u,v,h)) or not ((h>=20)&(h<=200)).all() or not 0<=alpha<=.5:
        raise ValueError("invalid hub inputs")
    return np.hypot(u,v)*(h/100)**alpha

def self_test():
    v=[0,3,3,12,25,25,30];p=[0,0,.1,2,2,0,0]
    x=[0,2.99,3,7.5,12,24.999,25,25.001,30,31]
    np.testing.assert_allclose(capacity_factor(x,v,p),[0,0,.05,.525,1,1,0,0,0,0])
    np.testing.assert_allclose(hub_speed([3],[4],100),[5])
    np.testing.assert_allclose(hub_speed([3],[4],50,.2),[5*.5**.2])
    for bad in ([0,4,3],[0,float("nan"),4]):
        try:capacity_factor([3],bad,[0,1,0])
        except ValueError:pass
        else:raise AssertionError("invalid curve accepted")
    print("wind_curve_kernel_tests_passed")
if __name__=="__main__":self_test()
