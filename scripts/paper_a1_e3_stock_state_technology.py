"""Technology decomposition of exact-key OP stock changes using side-specific labels."""
import argparse,csv,json
from pathlib import Path
import duckdb
from paper_a1_capacity_breakdown import URL
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    con=duckdb.connect()
    con.execute(f"""CREATE TEMP TABLE base AS SELECT year(report_date) yr,plant_id_eia plant,generator_id gen,
    operational_status_code status,coalesce(state,'Unknown') || '|' || coalesce(technology_description,'Unknown') tech,CAST(capacity_mw AS DOUBLE) mw
    FROM read_parquet('{URL}') WHERE year(report_date) BETWEEN 2023 AND 2025""")
    result=[]
    for y in (2023,2024):
        rows=con.execute("""WITH a AS (SELECT * FROM base WHERE yr=?),b AS (SELECT * FROM base WHERE yr=?),
        paired AS (SELECT a.gen ag,b.gen bg,a.status ast,b.status bst,a.tech AS earlier_tech,b.tech AS later_tech,a.mw am,b.mw bm
        FROM a FULL OUTER JOIN b ON a.plant=b.plant AND a.gen=b.gen),
        classified AS (SELECT *,CASE WHEN ag IS NULL THEN 'later_only' WHEN bg IS NULL THEN 'earlier_only'
        WHEN ast='OP' AND bst='OP' THEN 'matched_OP_both' WHEN ast='OP' THEN 'matched_exit_OP'
        WHEN bst='OP' THEN 'matched_enter_OP' ELSE 'neither_OP' END category FROM paired),
        contributions AS (SELECT category,earlier_tech AS tech,am earlier_mw,0.0 later_mw FROM classified WHERE ast='OP'
        UNION ALL SELECT category,later_tech,0.0,bm FROM classified WHERE bst='OP')
        SELECT category,tech,sum(earlier_mw),sum(later_mw) FROM contributions GROUP BY ALL ORDER BY 1,2""",[y,y+1]).fetchall()
        for cat,tech,a,b in rows:
            result.append(dict(year_a=y,year_b=y+1,category=cat,state=tech.split('|',1)[0],technology=tech.split('|',1)[1],earlier_mw=a,later_mw=b,delta_mw=b-a))
    with (d/"e3_op_stock_accounting.csv").open(newline="") as f:
        baseline=list(csv.DictReader(f))
    for r in baseline:
        subset=[x for x in result if x["year_a"]==int(r["year_a"]) and x["category"]==r["category"]]
        for field,old in [("earlier_mw","earlier_known_OP_mw"),("later_mw","later_known_OP_mw")]:
            if abs(sum(x[field] for x in subset)-float(r[old]))>0.001:
                raise ValueError("Technology reconciliation failed")
    with (d/"e3_op_stock_by_state_technology.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    print(json.dumps(result))
if __name__=="__main__":
    main()
