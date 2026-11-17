"""Run pinned PUDL annual coverage and EIA-860 evidence matrix as one fail-closed pipeline.

Does not download data, infer commissioning, or approve empirical dispatch.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annual-csv", required=True)
    parser.add_argument("--targets", default="data/pudl/project_a_pudl_29_targets.csv")
    parser.add_argument("--release", required=True)
    parser.add_argument("--sha256", required=True, help="Expected source SHA256, fixed independently")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    annual = Path(args.annual_csv).resolve()
    targets = Path(args.targets).resolve()
    output = Path(args.out_dir).resolve()
    if not annual.is_file() or not targets.is_file():
        parser.error("Annual source and target cohort must be existing local files")
    if output == root or output == root / "data":
        parser.error("Choose a separate output directory")
    if len(args.sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in args.sha256):
        parser.error("Expected 64-character source SHA256")
    actual = hashlib.sha256(annual.read_bytes()).hexdigest()
    if actual.lower() != args.sha256.lower():
        parser.error("Pinned annual CSV SHA256 mismatch")
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / "pudl_annual_coverage.json"
    matrix = output / "pudl_eia860_87_row_evidence_matrix.json"
    subprocess.run([sys.executable, str(root / "scripts/audit_pudl_annual_coverage.py"),
                    "--annual-csv", str(annual), "--targets", str(targets),
                    "--output", str(receipt), "--release", args.release,
                    "--sha256", args.sha256], check=True)
    subprocess.run([sys.executable, str(root / "scripts/build_pudl_annual_eia860_evidence_matrix.py"),
                    "--coverage-json", str(receipt), "--annual-csv", str(annual),
                    "--targets", str(targets), "--output", str(matrix)], check=True)
    result = json.loads(matrix.read_text())
    if result["target_year_rows"] != 87 or result["empirical_dispatch_approved"] is not False:
        raise RuntimeError("Unsafe evidence matrix output")
    print(json.dumps({"coverage": str(receipt), "matrix": str(matrix),
                      "rows": 87, "empirical_dispatch_approved": False}, indent=2))


if __name__ == "__main__":
    main()
