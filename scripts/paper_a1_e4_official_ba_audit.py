"""Compare PUDL generator BA labels against pinned official EIA-860 plant worksheets."""
import argparse,csv,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
from openpyxl import load_workbook
import duckdb
from paper_a1_e2_official_archive_audit import ARCHIVES
from paper_a1_capacity_breakdown import URL
def norm(x):return " ".join(str(x or "").strip().lower().split())
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir
    con=duckdb.connect()
    con.execute("CREATE TABLE official(yr INTEGER,plant INTEGER,ba VARCHAR,workbook VARCHAR,worksheet VARCHAR,excel_row INTEGER)")
    for y,(url,sha) in ARCHIVES.items():
        with urllib.request.urlopen(url,timeout=120) as f:raw=f.read()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("archive hash mismatch")
        rows=[]
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for name in z.namelist():
                if "plant" not in name.lower() or not name.lower().endswith(".xlsx"):continue
                wb=load_workbook(io.BytesIO(z.read(name)),read_only=True,data_only=True)
                for ws in wb:
                    pi=bi=None
                    for i,row in enumerate(ws.iter_rows(values_only=True),1):
                        if pi is None:
                            labels=[norm(v) for v in row]
                            candidates=[j for j,v in enumerate(labels) if "balancing authority" in v and "code" in v]
                            if "plant code" in labels and len(candidates)==1:pi=labels.index("plant code");bi=candidates[0]
                            elif i>=15:break
                            continue
                        try:plant=int(row[pi])
                        except (TypeError,ValueError):continue
                        ba=str(row[bi] or "").strip() or None
                        rows.append((y,plant,ba,name,ws.title,i))
                wb.close()
        if not rows:raise ValueError(f"No official BA rows {y}")
        con.executemany("INSERT INTO official VALUES (?,?,?,?,?,?)",rows)
    con.execute(f"""CREATE TABLE comparison AS WITH o AS (SELECT yr,plant,count(*) n,count(DISTINCT ba) distinct_ba,min(ba) ba FROM official GROUP BY 1,2)
    SELECT year(g.report_date) yr,g.plant_id_eia plant,g.generator_id gen,g.capacity_mw mw,
    nullif(trim(g.balancing_authority_code_eia),'') pudl_ba,o.ba official_ba,
    CASE WHEN o.plant IS NULL THEN 'official_plant_absent' WHEN o.distinct_ba>1 THEN 'official_conflict'
    WHEN o.ba IS NULL THEN 'official_ba_missing' WHEN nullif(trim(g.balancing_authority_code_eia),'') IS NULL THEN 'pudl_ba_missing'
    WHEN trim(g.balancing_authority_code_eia)=o.ba THEN 'agree' ELSE 'disagree' END status
    FROM read_parquet('{URL}') g LEFT JOIN o ON year(g.report_date)=o.yr AND g.plant_id_eia=o.plant
    WHERE year(g.report_date) BETWEEN 2023 AND 2025 AND g.operational_status_code='OP'""")
    for table in ("official","comparison"):
        con.execute(f"COPY {table} TO '{d}/e4_ba_{table}.csv' (HEADER, DELIMITER ',')")
    cur=con.execute("SELECT yr,coalesce(pudl_ba,'Unknown') ba,status,count(*) records,sum(mw) mw FROM comparison GROUP BY ALL ORDER BY 1,2,3")
    cols=[x[0] for x in cur.description];rows=[dict(zip(cols,r)) for r in cur.fetchall()]
    (d/"e4_ba_official_audit.json").write_text(json.dumps(rows,indent=2))
    print(json.dumps(rows))
if __name__=="__main__":main()
