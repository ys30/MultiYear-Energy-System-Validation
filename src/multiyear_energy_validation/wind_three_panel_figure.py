"""Publication-oriented, dependency-free SVG summary of verified R02 diagnostics."""
import json
from pathlib import Path

ROOT=Path("outputs/spatial_weather_merged_2025")
IDS=("57484","57514","7526")
COLORS={"57484":"#3265a8","57514":"#d17b32","7526":"#329477"}

def svg_chart(comp,loo,matched):
    cm={s["plant_id"]:s["metrics"] for s in comp["sites"]}
    lm={(s["plant_id"],s["year"]):s for s in loo["sites"]}
    mm={s["plant_id"]:s["matched_month_year_difference_pearson_r"] for s in matched["sites"]}
    chunks=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="540" viewBox="0 0 1120 540">',
      '<rect width="1120" height="540" fill="white"/>',
      '<style>text{font-family:Arial,sans-serif;fill:#273344}.title{font-size:19px;font-weight:bold}.sub{font-size:13px}.tick{font-size:12px}</style>',
      '<text x="35" y="34" class="title">Wind resource–generation association | 2024–2025</text>',
      '<text x="35" y="55" class="sub">NASA POWER WS10M vs EIA-923 observed daily-normalized monthly generation (Pearson r)</text>']
    panels=[(30,"A  Annual monthly association"),(400,"B  Leave-one-month-out ranges"),(770,"C  Matched-month year contrasts")]
    for left,title in panels:
        chunks.append(f'<text x="{left+12}" y="94" class="title">{title}</text>')
        for tick in (0,.25,.5,.75,1):
            y=420-260*tick
            chunks.append(f'<line x1="{left+45}" y1="{y}" x2="{left+325}" y2="{y}" stroke="#e2e6eb"/>')
            chunks.append(f'<text x="{left+6}" y="{y+4}" class="tick">{tick:.2f}</text>')
        chunks.append(f'<line x1="{left+45}" y1="160" x2="{left+45}" y2="420" stroke="#6a7480"/>')
    for i,pid in enumerate(IDS):
        color=COLORS[pid]
        # Panel A: two circles, each site pair
        x=30+90+i*84
        key="monthly_mean_ws10m_vs_daily_normalized_generation_pearson"
        for year,dx in ((2024,-13),(2025,13)):
            r=cm[pid][key][str(year)]
            fill = color if year == 2025 else "white"
            chunks.append(f'<circle cx="{x+dx}" cy="{420-260*r:.2f}" r="7" fill="{fill}" stroke="{color}" stroke-width="2"/>')
        chunks.append(f'<text x="{x}" y="443" class="tick" text-anchor="middle">{pid}</text>')
        # Panel B: ranges for each year
        x=400+90+i*84
        for year,dx in ((2024,-12),(2025,12)):
            s=lm[(pid,year)]
            lo=420-260*s["leave_one_month_out_min_r"]
            hi=420-260*s["leave_one_month_out_max_r"]
            width = 6 if year == 2025 else 3
            dash = "none" if year == 2025 else "3,3"
            chunks.append(f'<line x1="{x+dx}" y1="{lo:.2f}" x2="{x+dx}" y2="{hi:.2f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" stroke-linecap="round"/>')
            full = cm[pid][key][str(year)]
            marker_fill = color if year == 2025 else "white"
            chunks.append(f'<circle cx="{x+dx}" cy="{420-260*full:.2f}" r="5" fill="{marker_fill}" stroke="{color}" stroke-width="2"/>')
        chunks.append(f'<text x="{x}" y="443" class="tick" text-anchor="middle">{pid}</text>')
        # Panel C: same-month year contrast
        x=770+90+i*84;r=mm[pid]
        chunks.append(f'<rect x="{x-15}" y="{420-260*r:.2f}" width="30" height="{260*r:.2f}" fill="{color}" opacity=".82"/>')
        chunks.append(f'<text x="{x}" y="443" class="tick" text-anchor="middle">{pid}</text>')
        chunks.append(f'<text x="{x}" y="{408-260*r:.2f}" class="tick" text-anchor="middle">{r:.3f}</text>')
    chunks+=['<circle cx="43" cy="465" r="6" fill="white" stroke="#3265a8" stroke-width="2"/>',
             '<text x="55" y="469" class="tick">2024 (open dots / dashed ranges)</text>',
             '<circle cx="405" cy="465" r="6" fill="#3265a8" stroke="#3265a8" stroke-width="2"/>',
             '<text x="417" y="469" class="tick">2025 (filled dots / solid ranges)</text>',
             '<text x="35" y="485" class="sub">Colors identify plants. In B, dots show full-sample r; ranges are sensitivity, NOT confidence intervals.</text>',
             '<text x="35" y="503" class="sub">Descriptive associations only; 12 months/year, 11-month leave-one-out subsets. Not causal or out-of-sample prediction.</text>',
             '<text x="35" y="522" class="sub">10 m wind is not turbine hub-height wind; curtailment, maintenance and capacity changes remain uncontrolled.</text>',
             '</svg>']
    return "\n".join(chunks)+"\n"

def main():
    read=lambda name:json.loads((ROOT/name).read_text(encoding="utf-8"))
    svg=svg_chart(read("wind_2024_2025_comparison.json"),
                  read("wind_2024_2025_leave_one_month_out.json"),
                  read("wind_2024_2025_matched_month_contrasts.json"))
    path=ROOT/"wind_2024_2025_three_panel.svg"
    path.write_text(svg,encoding="utf-8")
    print("WIND_THREE_PANEL_FIGURE="+str(path))

if __name__=="__main__":main()
