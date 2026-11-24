"""Verify official EIA-860 annual ZIP bytes against frozen hashes; no lineage inferred."""
import argparse
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

ARCHIVES={
  2023:("https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602023.zip",
        "1447e23e608bea1523961542a90eb93ea86715067a37f211282541461049b46f"),
  2024:("https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip",
        "0aaae04812cd4ab87a3e346bdf93848a3cc15053fd4dc2a4cf82d2aeac95f12b"),
  2025:("https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip",
        "2b27929d26cc1da9ad6a530da1cac6718cd8496098ee560c4d47cfffd96d08ba")
}

def audit(year,folder):
    url,expected=ARCHIVES[year]
    request=urllib.request.Request(url,headers={"User-Agent":"ResearchArchiveAudit/1.0"})
    with urllib.request.urlopen(request,timeout=90) as response:
        raw=response.read()
    observed=hashlib.sha256(raw).hexdigest()
    if observed!=expected:
        raise ValueError(f"Official EIA-{year} archive SHA256 mismatch; stop before parsing: expected={expected} observed={observed}")
    target=folder/f"eia860{year}.zip"
    target.write_bytes(raw)
    with zipfile.ZipFile(target) as z:
        members=[{"name":i.filename,"size_bytes":i.file_size} for i in z.infolist() if not i.is_dir()]
        bad=z.testzip()
        if bad is not None:
            raise ValueError(f"Corrupt member: {bad}")
    target.unlink()  # Do not upload raw source ZIPs as workflow artifacts.
    return {"year":year,"url":url,"sha256":observed,"size_bytes":len(raw),
            "archive_verified":True,"members":members,
            "official_generator_rows_located":0,"physical_lineage_links_verified":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--years",type=int,nargs="+",default=[2023,2024,2025])
    args=p.parse_args()
    folder=args.output_dir
    folder.mkdir(parents=True,exist_ok=True)
    report=[]
    for year in args.years:
        if year not in ARCHIVES:
            raise ValueError(f"Unsupported year {year}")
        report.append(audit(year,folder))
    (folder/"e2_official_eia860_archive_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps([{"year":x["year"],"sha256":x["sha256"],
      "member_count":len(x["members"]),"official_generator_rows_located":0} for x in report],indent=2))

if __name__=="__main__":
    main()
