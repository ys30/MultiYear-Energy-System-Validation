"""Inventory independently downloaded official EIA-860 annual ZIP archives.

This is a source-discovery step, NOT an exact-key comparison or commissioning gate.
"""
import argparse
import hashlib
import json
import re
import urllib.request
import zipfile
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True)
    p.add_argument("--years", nargs="+", type=int, default=[2023, 2024, 2025])
    args = p.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    receipts = []
    for year in args.years:
        if year not in (2023, 2024, 2025):
            p.error("Only explicitly scoped annual years 2023–2025 allowed")
        url = f"https://www.eia.gov/electricity/data/eia860/xls/eia860{year}.zip"
        dest = out / f"eia860{year}.zip"
        req = urllib.request.Request(url, headers={"User-Agent": "ProjectA-Annual-EIA860-Research/1.0"})
        with urllib.request.urlopen(req, timeout=90) as response, dest.open("wb") as stream:
            if response.status != 200:
                raise RuntimeError(f"{year}: HTTP {response.status}")
            import shutil
            shutil.copyfileobj(response, stream)
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        with zipfile.ZipFile(dest) as z:
            if z.testzip() is not None:
                raise RuntimeError(f"{year}: corrupt ZIP")
            members = []
            for info in z.infolist():
                if info.is_dir():
                    continue
                if info.file_size > 150_000_000:
                    raise RuntimeError(f"{year}: unexpectedly large ZIP member")
                members.append({"name": info.filename, "size": info.file_size})
            generator_candidates = [m["name"] for m in members if
                                    re.search(r"generator", m["name"], re.IGNORECASE)
                                    and m["name"].lower().endswith((".xlsx", ".xls"))]
        receipts.append({"year": year, "source_url": url, "zip_sha256": digest,
                         "zip_bytes": dest.stat().st_size,
                         "members": members, "generator_candidates": generator_candidates,
                         "official_generator_rows_verified": False,
                         "physical_commissioning_verified": False,
                         "empirical_dispatch_approved": False})
        print(f"{year}: ZIP SHA256={digest}; generator workbook candidates={generator_candidates}", flush=True)
    (out / "official_eia860_archive_inventory.json").write_text(
        json.dumps({"schema_version": 1, "sources": receipts,
                    "exact_generator_identity_verified": False,
                    "empirical_dispatch_approved": False}, indent=2) + "\n")
    print("Official archive inventory complete; workbook row matching remains pending.")


if __name__ == "__main__":
    main()
