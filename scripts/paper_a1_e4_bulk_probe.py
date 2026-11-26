"""Probe official EIA-930 half-year bulk files, retaining source hashes and header evidence."""
import csv,hashlib,json,urllib.request,io,argparse
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument("--output-dir",type=Path,required=True);d=p.parse_args().output_dir;d.mkdir(parents=True,exist_ok=True)
    report=[]
    for year in (2024,2025):
        for half in ("Jan_Jun","Jul_Dec"):
            url=f"https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_{year}_{half}.csv"
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ResearchDataAudit/1.0"}),timeout=180) as f:raw=f.read()
                reader=csv.reader(io.StringIO(raw.decode("utf-8-sig")))
                header=next(reader)
                if not any("balancing authority" in x.lower() for x in header) or not any("utc" in x.lower() for x in header):raise ValueError("unexpected header")
                count=0;sample=[]
                for row in reader:
                    count+=1
                    if len(sample)<2:sample.append(row)
                report.append(dict(year=year,half=half,url=url,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),rows=count,header=header,sample=sample,status="retrieved"))
            except Exception as e:report.append(dict(year=year,half=half,url=url,status="blocked",error_type=type(e).__name__))
    (d/"bulk_probe.json").write_text(json.dumps(report,indent=2));print(json.dumps(report))
    if any(r["status"]!="retrieved" for r in report):raise SystemExit(1)
if __name__=="__main__":main()
