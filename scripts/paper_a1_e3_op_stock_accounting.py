"""Exact-key annual capacity accounting for OP records, not physical lineage."""
import argparse,csv,json
from pathlib import Path
import duckdb
from paper_a1_capacity_breakdown import URL

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    d=p.parse_args().output_dir
    con=duckdb.connect()
    con.execute(f"""CREATE TEMP TABLE base AS SELECT year(report_date) yr, plant_id_eia plant,
        generator_id gen, operational_status_code status, CAST(capacity_mw AS DOUBLE) mw
        FROM read_parquet('{URL}') WHERE year(report_date) BETWEEN 2023 AND 2025""")
    if con.execute("SELECT count(*) FROM (SELECT yr,plant,gen FROM base GROUP BY ALL HAVING count(*)>1)").fetchone()[0]:
        raise ValueError("Duplicate exact keys")
    result=[]
    for y in (2023,2024):
        rows=con.execute("""WITH a AS (SELECT * FROM base WHERE yr=?),
        b AS (SELECT * FROM base WHERE yr=?),
        paired AS (SELECT a.gen ag,b.gen bg,a.status ast,b.status bst,a.mw am,b.mw bm
        FROM a FULL OUTER JOIN b ON a.plant=b.plant AND a.gen=b.gen),
        classified AS (SELECT *,CASE WHEN ag IS NULL THEN 'later_only'
        WHEN bg IS NULL THEN 'earlier_only'
        WHEN ast='OP' AND bst='OP' THEN 'matched_OP_both'
        WHEN ast='OP' THEN 'matched_exit_OP'
        WHEN bst='OP' THEN 'matched_enter_OP' ELSE 'neither_OP' END category
        FROM paired)
        SELECT category,count(*),
        count(*) FILTER(WHERE (ast='OP' AND am IS NULL) OR (bst='OP' AND bm IS NULL)),
        sum(CASE WHEN ast='OP' THEN coalesce(am,0) ELSE 0 END),
        sum(CASE WHEN bst='OP' THEN coalesce(bm,0) ELSE 0 END)
        FROM classified GROUP BY category ORDER BY category""",[y,y+1]).fetchall()
        for category,n,missing,a,b in rows:
            result.append(dict(year_a=y,year_b=y+1,category=category,records=n,missing_OP_capacity=missing,
                earlier_known_OP_mw=a,later_known_OP_mw=b,known_OP_delta_mw=b-a))
        expected=con.execute("SELECT yr,sum(mw) FROM base WHERE status='OP' AND yr IN (?,?) GROUP BY yr ORDER BY yr",[y,y+1]).fetchall()
        subset=[r for r in result if r["year_a"]==y]
        for field,target in zip(("earlier_known_OP_mw","later_known_OP_mw"),[x[1] for x in expected]):
            if abs(sum(r[field] for r in subset)-target)>0.001:
                raise ValueError("OP stock reconciliation failed")
    with (d/"e3_op_stock_accounting.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]))
        w.writeheader()
        w.writerows(result)
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
