"""Build a paper-facing evidence manifest strictly from regenerated R02 outputs."""
import json
from pathlib import Path
from .wind_svg_numeric_audit import reconcile, KEY

def build_manifest(registry, readiness, comparison, matched, svg_audit):
    sites=registry["sites"]
    if readiness["summary"]["plant_count"]!=len(sites):
        raise ValueError("plant count mismatch")
    slots=sum(len(s["engineering_parameters"]) for s in sites)
    if readiness["summary"]["total_gates"]!=slots+5:
        raise ValueError("gate count mismatch")
    if readiness["summary"]["decision_counts"]["block"]!=slots+5:
        raise ValueError("unexpected baseline gate decisions")
    if readiness["summary"]["empirical_dispatch_approved"]:
        raise ValueError("dispatch approval not supported")
    comp={str(s["plant_id"]):s["metrics"][KEY] for s in comparison["sites"]}
    pairs={str(s["plant_id"]):s for s in matched["sites"]}
    if set(comp)!=set(pairs) or len(comp)!=3:
        raise ValueError("wind cohort mismatch")
    if svg_audit["numeric_checks"]!=21 or not svg_audit["reconciled"]:
        raise ValueError("figure reconciliation incomplete")
    wind=[]
    for pid in sorted(comp):
        x=pairs[pid]
        wind.append({"plant_id":pid,"within_year_pearson_r":{
            year:comp[pid][year] for year in ("2024","2025")},
            "matched_month_pearson_r":x["matched_month_year_difference_pearson_r"],
            "matched_month_lomo_min_r":x["matched_month_leave_one_out_min_r"],
            "matched_month_lomo_max_r":x["matched_month_leave_one_out_max_r"]})
    return {"schema_version":"1.0","source_files":[
        "plant_parameter_provenance.json","empirical_dispatch_readiness_v2.json",
        "wind_2024_2025_comparison.json","wind_2024_2025_matched_month_contrasts.json",
        "wind_2024_2025_three_panel.svg"],
        "pilot":{"plants":len(sites),"solar":sum(s["technology"]=="solar" for s in sites),
                 "wind":sum(s["technology"]=="wind" for s in sites),
                 "engineering_parameter_slots":slots},
        "readiness":readiness["summary"],"wind_diagnostics":wind,
        "figure_audit":svg_audit,
        "limitations":["not empirical hourly dispatch validation",
                       "not a complete historical source coverage census",
                       "LOMO ranges are not confidence intervals"]}

def main():
    root=Path("outputs/spatial_weather_merged_2025")
    load=lambda n:json.loads((root/n).read_text(encoding="utf-8"))
    result=build_manifest(load("plant_parameter_provenance.json"),
        load("empirical_dispatch_readiness_v2.json"),
        load("wind_2024_2025_comparison.json"),
        load("wind_2024_2025_matched_month_contrasts.json"),reconcile(root))
    (root/"paper_evidence_manifest.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PAPER_EVIDENCE_MANIFEST="+json.dumps({
        "plants":result["pilot"]["plants"],
        "slots":result["pilot"]["engineering_parameter_slots"],
        "blocked":result["readiness"]["decision_counts"]["block"],
        "wind_plants":len(result["wind_diagnostics"]),
        "svg_checks":result["figure_audit"]["numeric_checks"]},sort_keys=True))

if __name__=="__main__":
    main()
