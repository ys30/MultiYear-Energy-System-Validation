"""Tests for the archived three-panel wind association figure."""
import pytest
from multiyear_energy_validation.wind_three_panel_figure import svg_chart

IDS=("57484","57514","7526")
KEY="monthly_mean_ws10m_vs_daily_normalized_generation_pearson"

def fixtures():
    comparison={"sites":[{"plant_id":pid,"metrics":{KEY:{"2024":0.7,"2025":0.8}}}
                         for pid in IDS]}
    loo={"sites":[{"plant_id":pid,"year":year,
                   "leave_one_month_out_min_r":0.6,
                   "leave_one_month_out_max_r":0.9}
                  for pid in IDS for year in (2024,2025)]}
    matched={"sites":[{"plant_id":pid,"matched_month_year_difference_pearson_r":0.75}
                      for pid in IDS]}
    return comparison,loo,matched

def test_svg_has_three_panels_and_all_plants():
    svg=svg_chart(*fixtures())
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    for title in ("Annual monthly association","Leave-one-month-out sensitivity",
                  "Matched-month year contrasts"):
        assert title in svg
    for pid in IDS:
        assert svg.count(f'>{pid}</text>')==3
    assert svg.count('>0.750</text>')==3
    assert svg.endswith('</svg>\n')

def test_missing_plant_rejected():
    comparison,loo,matched=fixtures()
    comparison["sites"].pop()
    with pytest.raises((KeyError,ValueError)):
        svg_chart(comparison,loo,matched)
