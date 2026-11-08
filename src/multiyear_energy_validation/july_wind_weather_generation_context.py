"""July 2025 wind weather-to-generation descriptive cross-section.

NASA POWER WS10M is not hub-height wind and is not a turbine power curve.
Three plants cannot establish a statistical weather-to-generation relationship.
"""
import csv
import json
from pathlib import Path

WIND_IDS=("57484","57514","7526")


def july_wind_context(weather_root, capacity_audit, output_path):
    by_id={s["plant_id"]:s for s in capacity_audit["sites"]}
    out=[]
    for pid in WIND_IDS:
        files=list(Path(weather_root).glob(f"wind_plant_{pid}_july2025.csv"))
        if len(files)!=1: raise ValueError(f"expected one weather file for {pid}: {files}")
        with files[0].open(newline="",encoding="utf-8") as stream:
            rows=list(csv.DictReader(stream))
        if len(rows)!=744 or len({r["period_utc"] for r in rows})!=744:
            raise ValueError(f"incomplete July UTC weather for {pid}")
        wind=[float(r["wind_speed_10m_ms"]) for r in rows]
        if any(v<0 or v>100 for v in wind): raise ValueError(f"invalid WS10M for {pid}")
        site=by_id[pid]
        out.append({
            "plant_id":pid,"weather_hours":744,
            "nasa_power_ws10m_mean_ms":round(sum(wind)/len(wind),6),
            "nasa_power_ws10m_mean_cubed_ms3":round(sum(v**3 for v in wind)/len(wind),6),
            "observed_july_net_generation_mwh":site["net_generation_mwh"],
            "observed_july_net_capacity_factor":site["monthly_net_capacity_factor"],
            "source_weather_file":str(files[0]),
            "wind_speed_not_hub_height":True,
            "wind_cubed_proxy_not_power":True,
        })
    result={"month":"2025-07","sites":out,
            "sample_size_sites":3,
            "descriptive_cross_section_only":True,
            "meteorology_does_not_establish_causal_generation_explanation":True,
            "hourly_availability_approved":False,"empirical_dispatch_approved":False}
    target=Path(output_path);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("JULY_WIND_WEATHER_GENERATION_CONTEXT="+json.dumps(result,sort_keys=True))
    return result


if __name__=="__main__":
    root=Path("outputs/spatial_weather_merged_2025")
    audit=json.loads((root/"eia923_july2025_capacity_factor_audit.json").read_text(encoding="utf-8"))
    july_wind_context("outputs/spatial_weather_pilot_2025",audit,
                      root/"july_wind_weather_generation_context.json")
