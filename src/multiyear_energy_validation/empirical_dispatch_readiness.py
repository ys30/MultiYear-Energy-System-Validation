"""Conservative, machine-readable empirical-dispatch readiness assessment.

A registry entry with a documented parameter is evidence for that parameter,
not evidence that hourly renewable availability or dispatch is validated.
"""
import json
from pathlib import Path

SYSTEM_GATES = (
    ("hourly_renewable_availability", "plant-hour", "validated plant-specific hourly generation or availability"),
    ("generator_marginal_cost", "generator-hour or justified scenario", "source-reviewed fuel and operating costs"),
    ("storage_efficiency_and_soc", "storage-hour", "storage efficiencies, initial SOC and energy constraints"),
    ("transmission_and_interchange", "network-hour", "network limits and external interchange constraints"),
    ("hourly_dispatch_observation", "system-hour", "independent observed dispatch for evaluation"),
)

def assess_readiness(registry):
    if not isinstance(registry.get("sites"),list) or not registry["sites"]:
        raise ValueError("nonempty site registry required")
    rows=[]
    for site in registry["sites"]:
        pid=str(site["plant_id"])
        for name,entry in site["engineering_parameters"].items():
            status=entry.get("status","unknown")
            if status=="documented_plant_specific":
                ev=entry.get("source") or {}
                needed=("source_title","source_url","source_locator",
                        "equipment_applicability","effective_year","reviewer")
                documented=all(ev.get(k) not in (None,"") for k in needed) and entry.get("value") is not None
                decision="screen_only" if documented else "block"
                reason="documented engineering input; hourly availability still unvalidated" if documented else "incomplete evidence"
            elif status=="scenario_assumption":
                decision,reason="screen_only","scenario value is not a measured plant parameter"
            else:
                decision,reason="block","plant-specific engineering value unknown"
            rows.append({"scope":"plant","plant_id":pid,"technology":site["technology"],
                         "parameter":name,"status":status,"decision":decision,"reason":reason})
    for name,required,reason in SYSTEM_GATES:
        rows.append({"scope":"system","parameter":name,"required_resolution":required,
                     "status":"not_verified","decision":"block","reason":reason})
    summary={"plant_count":len(registry["sites"]),
             "plant_parameter_count":sum(x["scope"]=="plant" for x in rows),
             "blocked":sum(x["decision"]=="block" for x in rows),
             "screen_only":sum(x["decision"]=="screen_only" for x in rows),
             "empirical_dispatch_approved":False}
    return {"schema_version":"1.0","summary":summary,"gates":rows,
            "caveat":"EIA-923 monthly net generation does not validate hourly dispatch or renewable availability."}

def main():
    base=Path("outputs/spatial_weather_merged_2025")
    registry=json.loads((base/"plant_parameter_provenance.json").read_text(encoding="utf-8"))
    report=assess_readiness(registry)
    (base/"empirical_dispatch_readiness.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EMPIRICAL_DISPATCH_READINESS="+json.dumps(report["summary"],sort_keys=True))

if __name__=="__main__":
    main()
