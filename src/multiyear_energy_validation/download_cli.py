"""Explicit opt-in EIA API candidate snapshot download CLI."""
import argparse
import json
import os
from datetime import datetime, timezone

from .eia_snapshot import save_candidate_snapshot


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download unverified EIA candidate rows")
    parser.add_argument("--respondent", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-rows", type=int, default=20000)
    args = parser.parse_args(argv)
    key = os.environ.get("EIA_API_KEY")
    if not key:
        parser.error("EIA_API_KEY environment variable required; never put keys in CLI arguments")
    manifest = save_candidate_snapshot(
        args.output_dir, api_key=key, respondent=args.respondent,
        start=args.start, end=args.end, max_rows=args.max_rows,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
