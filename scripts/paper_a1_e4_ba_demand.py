"""BA demand acquisition adapted from Project B; no dispatch admission implied."""
import argparse, json, os, time, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd
API="https://api.eia.gov/v2/electricity/rto/region-data/data/"
DEFAULT_BAS=("CISO","ERCO","AZPS","PNM","PSCO","IPCO","PACW")
def fetch_eia_demand(year: int, bas=DEFAULT_BAS, api_key=None, length=5000):
    """Fetch EIA-930 hourly reported demand (MW), paginating with deterministic sorting."""
    key = api_key or os.getenv("EIA_API_KEY")
    if not key:
        raise ValueError("Set EIA_API_KEY. An EIA API key is required for this workflow.")
    if not bas:
        raise ValueError("At least one balancing authority is required")
    if len(set(bas)) != len(bas) or any(not isinstance(ba, str) or not ba.strip() or ba != ba.strip() for ba in bas):
        raise ValueError("BA selection must contain unique, nonblank, whitespace-free codes")
    params = [
        ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[type][]", "D"), ("start", f"{year}-01-01T00"),
        ("end", f"{year}-12-31T23"), ("length", str(length)),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("sort[1][column]", "respondent"), ("sort[1][direction]", "asc"),
    ]
    params += [("facets[respondent][]", ba) for ba in bas]
    offset = 0
    frames = []
    total = None
    while total is None or offset < total:
        query = urllib.parse.urlencode(params + [("offset", str(offset))])
        request = urllib.request.Request(API + "?" + query,
                                         headers={"User-Agent": "pypsa-western-us-research/0.1"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = json.load(response)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        result = payload.get("response", {})
        if "data" not in result:
            raise ValueError(f"EIA response missing data: {str(payload)[:250]}")
        rows = result["data"]
        total = int(result.get("total", 0))
        if not rows:
            break
        frames.append(pd.DataFrame(rows))
        offset += len(rows)
    if not frames:
        raise ValueError(f"No EIA demand observations for {year} and {bas}")
    data = pd.concat(frames, ignore_index=True)
    require = {"period", "respondent", "value"}
    if not require.issubset(data.columns):
        raise ValueError(f"Missing fields: {require - set(data.columns)}")
    data = data[["period", "respondent", "value"]].copy()
    data["period"] = pd.to_datetime(data["period"], utc=True, errors="raise")
    data["value"] = pd.to_numeric(data["value"], errors="coerce").astype("float64")
    # Reject out-of-scope API rows instead of silently discarding them during
    # the expected BA-hour reindex (which could conceal upstream API changes).
    requested_bas = set(bas)
    unexpected_bas = set(data["respondent"].dropna()) - requested_bas
    if data["respondent"].isna().any() or unexpected_bas:
        raise ValueError(f"Unexpected or missing EIA demand BA identifiers: {sorted(unexpected_bas)}")
    year_start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    year_end = pd.Timestamp(f"{year+1}-01-01", tz="UTC")
    if data["period"].isna().any() or not data["period"].between(year_start, year_end, inclusive="left").all():
        raise ValueError("EIA demand API returned timestamps outside requested year")
    if data.duplicated(["period", "respondent"]).any():
        raise ValueError("Duplicate balancing authority-hour rows")
    # EIA publishes BA-level reported values as received, including anomalies.
    # Preserve observations and audit any replacement. Do not silently set negatives to zero.
    data = data.sort_values(["respondent", "period"]).reset_index(drop=True)
    # Reject concentrated nonpositive/missing values in reported rows before
    # creating the full-year grid. This also yields the correct diagnostic
    # for partial-year API fixtures with a known BA-specific anomaly.
    import numpy as np
    raw_bad = ~np.isfinite(data["value"]) | data["value"].le(0)
    raw_rates = data.assign(_bad=raw_bad).groupby("respondent")["_bad"].agg(["sum","count"])
    excessive_raw = raw_rates[raw_rates["sum"] / raw_rates["count"] > 0.01]
    if not excessive_raw.empty:
        raise ValueError("BA-specific EIA demand QC exceeds 1%: " + excessive_raw.to_json())
    # EIA-930 can omit individual BA-hour records entirely. Materialize those
    # as missing observations so the same audited short-gap rules apply.
    # Never invent a value or silently substitute another balancing authority.
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                             freq="h", inclusive="left", tz="UTC")
    required_pairs = pd.MultiIndex.from_product(
        [list(bas), expected], names=["respondent", "period"]
    )
    observed_pairs = pd.MultiIndex.from_frame(data[["respondent", "period"]])
    absent_pairs = required_pairs.difference(observed_pairs)
    if len(absent_pairs):
        print(f"EIA demand QC: {len(absent_pairs)} absent BA-hour API records; "
              f"examples={list(absent_pairs[:8])}", flush=True)
        if len(absent_pairs) / len(required_pairs) > 0.01:
            raise ValueError("More than 1% of BA-hour API records are absent")
        data = (data.set_index(["respondent", "period"])
                .reindex(required_pairs).reset_index())
    bad = ~np.isfinite(data["value"]) | (data["value"] <= 0)
    data["raw_value"] = data["value"]
    data["qc_flag"] = bad.map({True: "missing_or_nonpositive", False: "observed"})
    if len(absent_pairs):
        absent_mask = pd.MultiIndex.from_frame(
            data[["respondent", "period"]]
        ).isin(absent_pairs)
        data.loc[absent_mask, "qc_flag"] = "absent_api_record"
    # Enforce the QC threshold for EACH BA before attempting any imputation.
    # A concentrated failure must not be hidden by a pooled low anomaly rate.
    by_ba = data.assign(_bad=bad).groupby("respondent")["_bad"].agg(["sum", "count"])
    excessive = by_ba[by_ba["sum"] / by_ba["count"] > 0.01]
    if not excessive.empty:
        raise ValueError("BA-specific EIA demand QC exceeds 1%: " + excessive.to_json())
    n_bad = int(bad.sum())
    if n_bad:
        print(f"EIA demand QC: {n_bad} missing/nonpositive observations among {len(data)}", flush=True)
        # Diagnose consecutive missing blocks without modifying raw_values.
        # Short gaps <=3 hours use time interpolation; longer gaps up to 24h
        # use matching UTC hour on adjacent days (assumption, flagged).
        # A longer block is left unresolved and fails the run.
        for ba, idx in data.groupby("respondent").groups.items():
            subset = data.loc[idx].sort_values("period")
            vals = subset["value"].where(subset["value"] > 0).copy()
            missing = vals.isna()
            blocks = (missing != missing.shift(fill_value=False)).cumsum()
            for _, group in subset.loc[missing].groupby(blocks[missing]):
                positions = group.index
                length = len(positions)
                first = subset.index.get_loc(positions[0])
                last = subset.index.get_loc(positions[-1])
                before = first - 1
                after = last + 1
                if before < 0 or after >= len(subset):
                    continue
                # Demand must be consecutive hourly observations before imputing.
                periods = subset["period"].reset_index(drop=True)
                segment = periods.iloc[before:after + 1]
                if not segment.diff().dropna().eq(pd.Timedelta(hours=1)).all():
                    continue
                if length <= 3:
                    left = float(vals.iloc[before])
                    right = float(vals.iloc[after])
                    if pd.notna(left) and pd.notna(right):
                        for j, ix in enumerate(positions, 1):
                            data.loc[ix, "value"] = left + (right - left) * j / (length + 1)
                            data.loc[ix, "qc_flag"] = "interpolated_le3h"
                elif length <= 24:
                    # Same-hour previous/next day must both be observed.
                    for ix in positions:
                        pos = subset.index.get_loc(ix)
                        if pos - 24 < 0 or pos + 24 >= len(subset):
                            continue
                        prev = subset.iloc[pos - 24]
                        nxt = subset.iloc[pos + 24]
                        current = subset.loc[ix]
                        if (current["period"] - prev["period"] != pd.Timedelta(hours=24)
                            or nxt["period"] - current["period"] != pd.Timedelta(hours=24)):
                            continue
                        a = prev["raw_value"]
                        b = nxt["raw_value"]
                        if pd.notna(a) and pd.notna(b) and a > 0 and b > 0:
                            data.loc[ix, "value"] = (float(a) + float(b)) / 2
                            data.loc[ix, "qc_flag"] = "neighboring_day_imputation"
                # For gaps >24h, only use a bounded same-hour neighboring-week
                # estimate with *both* original observations present. A 48-hour
                # zero block is not accepted as actual load and remains flagged.
                elif length <= 48:
                    for ix in positions:
                        pos = subset.index.get_loc(ix)
                        if pos - 168 < 0 or pos + 168 >= len(subset):
                            continue
                        prev = subset.iloc[pos - 168]
                        nxt = subset.iloc[pos + 168]
                        current = subset.loc[ix]
                        if (current["period"] - prev["period"] != pd.Timedelta(hours=168)
                            or nxt["period"] - current["period"] != pd.Timedelta(hours=168)):
                            continue
                        a = prev["raw_value"]
                        b = nxt["raw_value"]
                        if pd.notna(a) and pd.notna(b) and a > 0 and b > 0:
                            data.loc[ix, "value"] = (float(a) + float(b)) / 2
                            data.loc[ix, "qc_flag"] = "neighboring_week_imputation"
                print(f"  BA={ba} gap start={group.period.min()} length={length}h "
                      f"remaining={int((data.loc[positions, 'value'].isna() | (data.loc[positions, 'value'] <= 0)).sum())}", flush=True)
        remaining = data["value"].isna() | (data["value"] <= 0)
        if remaining.any():
            examples = data.loc[remaining, ["period", "respondent", "raw_value"]].head(8).to_dict("records")
            raise ValueError(f"Unresolved EIA data quality: {int(remaining.sum())} rows; examples={examples}")
    data.attrs["qc_anomaly_rows"] = n_bad
    data.attrs["qc_fraction"] = n_bad / len(data)
    if n_bad / len(data) > 0.01:
        raise ValueError(f"Too many EIA anomalies: {n_bad}/{len(data)} > 1% QC limit")
    # A pooled threshold alone could conceal severe corruption in one small BA.
    by_ba = data.groupby("respondent").agg(
        rows=("value", "size"),
        anomalies=("qc_flag", lambda flags: int((flags != "observed").sum())),
    )
    by_ba["anomaly_share"] = by_ba.anomalies / by_ba.rows
    failed = by_ba.loc[by_ba.anomaly_share > 0.01]
    if not failed.empty:
        raise ValueError(f"BA-specific EIA QC anomaly rate > 1%: {failed.to_dict('index')}")
    present = set(data.respondent)
    if set(bas) - present:
        raise ValueError(f"Missing balancing authorities: {set(bas) - present}")
    # Verify full UTC hourly coverage, including absent timestamps shared by all BAs.
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                             freq="h", inclusive="left", tz="UTC")
    actual = pd.DatetimeIndex(data["period"].unique()).sort_values()
    if not actual.equals(expected):
        missing = expected.difference(actual)
        unexpected = actual.difference(expected)
        raise ValueError(
            f"Incomplete hourly timestamp coverage for {year}: "
            f"missing={len(missing)}, unexpected={len(unexpected)}; "
            f"examples={list(missing[:5])}"
        )
    coverage = data.groupby("period").respondent.nunique()
    if len(coverage) != len(expected) or coverage.min() != len(bas):
        # A missing API record is distinct from a reported zero or NaN.
        # Report exact BA/time pairs rather than silently forward-filling them.
        complete = pd.MultiIndex.from_product(
            [expected, list(bas)], names=["period", "respondent"]
        )
        observed = pd.MultiIndex.from_frame(data[["period", "respondent"]])
        missing_pairs = complete.difference(observed)
        samples = [(str(t), ba) for t, ba in missing_pairs[:12]]
        raise ValueError(
            f"Incomplete BA coverage: {len(missing_pairs)} absent BA-hour records; "
            f"examples={samples}"
        )
    return data.sort_values(["period", "respondent"]).reset_index(drop=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--years",nargs="+",type=int,default=[2024,2025])
    p.add_argument("--bas",nargs="+",default=list(DEFAULT_BAS))
    a=p.parse_args()
    d=a.output_dir
    d.mkdir(parents=True,exist_ok=True)
    report=[]
    if not os.getenv("EIA_API_KEY"):
        (d/"e4_demand_admission.json").write_text(json.dumps({"status":"blocked","reason":"EIA_API_KEY not configured"}))
        print("EIA demand blocked: key not configured")
        return
    for year in a.years:
        for ba in a.bas:
            try:
                x=fetch_eia_demand(year,(ba,))
                x.to_csv(d/f"e4_demand_{ba}_{year}.csv",index=False)
                report.append(dict(year=year,ba=ba,status="passed",hours=len(x),anomalies=int((x.qc_flag!="observed").sum()),peak_mw=float(x.value.max()),energy_mwh=float(x.value.sum())))
            except Exception as e:
                # Do not log exception URLs or payloads that might contain credentials.
                report.append(dict(year=year,ba=ba,status="blocked",error_type=type(e).__name__))
    (d/"e4_demand_admission.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
if __name__=="__main__":main()
