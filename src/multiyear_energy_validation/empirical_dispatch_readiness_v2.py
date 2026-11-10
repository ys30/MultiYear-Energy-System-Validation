"""Versioned applicability-aware empirical dispatch evidence audit.

Distinguishes unknown evidence, failed validation and requirements that do not
apply to the declared model scope. No inference of missing real-world data.
"""
import json
from pathlib import Path
from .empirical_dispatch_readiness import SYSTEM_GATES

STATES={"missing","unverified","validated","not_applicable"}
REQUIRED_EVIDENCE=("source_title","source_url","source_locator",
                   "equipment_applicability","effective_year","reviewer")

def assess_v2(registry, evidence=None, scope=None):
    if not registry.get("sites"):
        raise ValueError("nonempty registry required")
    evidence=evidence or {}
    scope=scope or {}
    required=set(name for name,_,_ in SYSTEM_GATES)
    unknown=set(evidence)-required
    if unknown:
        raise ValueError("unknown system gates: "+",".join(sorted(unknown)))
    rows=[]
    for site in registry["sites"]:
        for param,entry in site["engineering_parameters"].items():
            status=entry.get("status","unknown")
            source=entry.get("source") or {}
            documented=(status=="documented_plant_specific"
                        and entry.get("value") is not None
                        and all(source.get(k) not in (None,"") for k in REQUIRED_EVIDENCE)
                        and str(source.get("source_url","")).startswith(("https://","http://")))
            if documented:
                state,decision,reason="unverified","screen_only","documented but not independently validated for model"
            elif status=="scenario_assumption":
                state,decision,reason="unverified","screen_only","scenario assumption cannot validate empirical dispatch"
            elif status=="documented_plant_specific":
                state,decision,reason="unverified","block","incomplete documentation"
            else:
                state,decision,reason="missing","block","no reviewed plant-specific value"
            rows.append({"scope":"plant","plant_id":str(site["plant_id"]),
                         "technology":site["technology"],"parameter":param,
                         "evidence_state":state,"decision":decision,"reason":reason})
    for name,resolution,description in SYSTEM_GATES:
        item=evidence.get(name,{})
        state=item.get("state","missing")
        if state not in STATES:
            raise ValueError("invalid state for "+name)
        applicable=scope.get(name,True)
        if not isinstance(applicable,bool):
            raise ValueError("applicability must be boolean for "+name)
        if not applicable:
            justification=scope.get(name+"_justification") or {}
            if not all(justification.get(k) not in (None,"") for k in ("rationale","reviewer")):
                raise ValueError("nonapplicability requires rationale and reviewer: "+name)
            if state!="not_applicable":
                raise ValueError("explicit not_applicable state required for "+name)
            decision,reason="not_applicable","declared model scope excludes this requirement"
        else:
            if state=="not_applicable":
                raise ValueError("applicable requirement cannot be not_applicable: "+name)
            if state=="validated":
                ev=item.get("evidence") or {}
                if not all(ev.get(k) not in (None,"") for k in REQUIRED_EVIDENCE):
                    raise ValueError("validated claim lacks traceable evidence: "+name)
                if not str(ev["source_url"]).startswith(("https://","http://")):
                    raise ValueError("validated claim requires absolute source URL")
                decision,reason="screen_only","documented claim requires independent model-level review"
            else:
                decision,reason="block",description
        rows.append({"scope":"system","parameter":name,"required_resolution":resolution,
                     "evidence_state":state,"decision":decision,"reason":reason})
    counts={k:sum(row["decision"]==k for row in rows)
            for k in ("block","screen_only","not_applicable")}
    return {"schema_version":"2.0","gates":rows,"summary":{
        "plant_count":len(registry["sites"]),"total_gates":len(rows),
        "decision_counts":counts,"empirical_dispatch_approved":False},
        "policy":"Even validated individual inputs do not automatically approve empirical hourly dispatch."}

def main():
    base=Path("outputs/spatial_weather_merged_2025")
    registry=json.loads((base/"plant_parameter_provenance.json").read_text(encoding="utf-8"))
    report=assess_v2(registry)
    (base/"empirical_dispatch_readiness_v2.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("EMPIRICAL_DISPATCH_READINESS_V2="+json.dumps(report["summary"],sort_keys=True))

if __name__=="__main__":
    main()
