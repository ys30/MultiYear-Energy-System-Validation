"""CLI for candidate hourly-demand coverage audit; no automatic downloading."""
import argparse
import json

from .reporting import write_coverage_report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit a verified UTC hourly observed-demand CSV")
    parser.add_argument("--csv", required=True, help="Local CSV input; raw records are not copied")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--timestamp-column", required=True)
    parser.add_argument("--demand-column", required=True)
    parser.add_argument("--region-column")
    parser.add_argument("--region")
    parser.add_argument("--source-uri", required=True)
    parser.add_argument("--retrieved-at", required=True)
    parser.add_argument("--confirm-utc-interval-start", action="store_true")
    parser.add_argument("--confirm-observed-demand-mw", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_utc_interval_start or not args.confirm_observed_demand_mw:
        parser.error("explicit UTC interval-start and observed-demand MW confirmations are required")
    if args.region and not args.region_column:
        parser.error("--region requires --region-column")
    report = write_coverage_report(
        args.csv, args.output_dir, year=args.year,
        timestamp_column=args.timestamp_column,
        demand_column=args.demand_column,
        region_column=args.region_column, region=args.region,
        source_uri=args.source_uri, retrieved_at=args.retrieved_at,
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
