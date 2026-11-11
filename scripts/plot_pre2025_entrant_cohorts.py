"""Generate Project A reported-operating-year cohort figure from audited 29-row CSV."""
import argparse
import csv
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot(source, output):
    with open(source, newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 29:
        raise ValueError(f"Expected 29 rows, got {len(rows)}")
    years = sorted({int(r["reported_operating_year"]) for r in rows})
    statuses = ("OP", "OS", "SB")
    counts = {s: [sum(int(r["reported_operating_year"]) == y and r["status_2025"] == s
                      for r in rows) for y in years] for s in statuses}
    mw = [sum(float(r["op_nameplate_mw_2025"]) for r in rows
              if int(r["reported_operating_year"]) == y) for y in years]
    if sum(sum(v) for v in counts.values()) != 29 or abs(sum(mw)-138.1) > 1e-6:
        raise ValueError("Source cohort count or OP MW failed validation")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bottom = [0] * len(years)
    for status in statuses:
        values = counts[status]
        ax.bar([str(y) for y in years], values, bottom=bottom, label=status, width=.66)
        bottom = [a+b for a,b in zip(bottom,values)]
    for i,(n,m) in enumerate(zip(bottom,mw)):
        ax.text(i,n+.15,f"{m:g} MW",ha="center",va="bottom",fontsize=9)
    ax.set_ylim(0,13.5)
    ax.set_ylabel("Generator records first appearing in 2025 CISO inventory")
    ax.set_xlabel("Reported operating year (not inventory-entry year)")
    ax.legend(frameon=False,ncol=3)
    ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,dpi=180)
    plt.close(fig)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default="data/pudl/project_a_pudl_29_targets.csv")
    parser.add_argument("--output",default="figures/project_a_pre2025_entrants.png")
    args=parser.parse_args()
    plot(args.source,args.output)
