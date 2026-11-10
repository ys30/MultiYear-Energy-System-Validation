"""Independent numeric reconciliation of SVG coordinates against source JSON.

The SVG itself is parsed as XML. All plotted plant/year values are checked
against their corresponding source estimates, not hardcoded manuscript values.
"""
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

from .wind_three_panel_figure import ROOT, IDS

NS="{http://www.w3.org/2000/svg}"
KEY="monthly_mean_ws10m_vs_daily_normalized_generation_pearson"

def near(a,b,tol=0.025):
    return math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol)

def reconcile(root=ROOT):
    root=Path(root)
    load=lambda name:json.loads((root/name).read_text(encoding="utf-8"))
    comp=load("wind_2024_2025_comparison.json")
    loo=load("wind_2024_2025_leave_one_month_out.json")
    matched=load("wind_2024_2025_matched_month_contrasts.json")
    svg=ET.fromstring((root/"wind_2024_2025_three_panel.svg").read_text(encoding="utf-8"))
    circles=list(svg.iter(NS+"circle"))
    lines=list(svg.iter(NS+"line"))
    rects=list(svg.iter(NS+"rect"))
    texts=list(svg.iter(NS+"text"))
    cm={str(s["plant_id"]):s["metrics"][KEY] for s in comp["sites"]}
    lm={(str(s["plant_id"]),int(s["year"])):s for s in loo["sites"]}
    mm={str(s["plant_id"]):s for s in matched["sites"]}
    assert set(cm)==set(lm_pid for lm_pid,_ in lm)==set(mm)==set(IDS)
    checks=0
    for i,pid in enumerate(IDS):
        color={"57484":"#3265a8","57514":"#d17b32","7526":"#329477"}[pid]
        for year,dx in ((2024,-13),(2025,13)):
            x=30+90+i*84+dx
            y=420-260*float(cm[pid][str(year)])
            assert any(near(el.get("cx"),x) and near(el.get("cy"),y)
                       and el.get("stroke")==color for el in circles)
            checks+=1
        for year,dx in ((2024,-12),(2025,12)):
            x=400+90+i*84+dx
            s=lm[(pid,year)]
            ys=sorted((420-260*float(s["leave_one_month_out_min_r"]),
                       420-260*float(s["leave_one_month_out_max_r"])))
            assert any(near(el.get("x1"),x) and near(el.get("x2"),x)
                       and near(min(float(el.get("y1")),float(el.get("y2"))),ys[0])
                       and near(max(float(el.get("y1")),float(el.get("y2"))),ys[1])
                       and el.get("stroke")==color for el in lines)
            checks+=1
        x=770+90+i*84
        s=mm[pid]
        value=float(s["matched_month_year_difference_pearson_r"])
        assert any(near(el.get("x"),x-15) and near(el.get("y"),420-260*value)
                   and near(el.get("height"),260*value) and el.get("fill")==color
                   for el in rects)
        checks+=1
        lo=float(s["matched_month_leave_one_out_min_r"])
        hi=float(s["matched_month_leave_one_out_max_r"])
        assert any(near(el.get("x1"),x) and near(el.get("x2"),x)
                   and near(el.get("y1"),420-260*lo)
                   and near(el.get("y2"),420-260*hi)
                   for el in lines)
        checks+=1
        assert any(el.text==f"{value:.3f}" for el in texts)
        checks+=1
    return {"plants":len(IDS),"numeric_checks":checks,"reconciled":True}

def main():
    result=reconcile()
    print("WIND_SVG_NUMERIC_AUDIT="+json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
