"""Tests for the archived three-panel wind association figure."""
import pytest
import xml.etree.ElementTree as ET
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
    matched={"sites":[{"plant_id":pid,"matched_month_year_difference_pearson_r":0.75,"matched_month_leave_one_out_min_r":0.65,"matched_month_leave_one_out_max_r":0.85}
                      for pid in IDS]}
    return comparison,loo,matched

def test_svg_has_three_panels_and_all_plants():
    svg=svg_chart(*fixtures())
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    for title in ("Annual monthly association","Leave-one-month-out ranges",
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


def test_svg_is_well_formed_and_year_styles_distinct():
    svg=svg_chart(*fixtures())
    root=ET.fromstring(svg)
    assert root.tag.endswith("svg")
    circles=[e for e in root.iter() if e.tag.endswith("circle")]
    assert any(e.attrib.get("fill")=="white" for e in circles)
    assert any(e.attrib.get("fill")=="#3265a8" for e in circles)
    assert "2024 (open dots" in svg
    assert "2025 (filled dots" in svg


def test_leave_one_out_ranges_are_not_labeled_confidence_intervals():
    svg=svg_chart(*fixtures())
    assert 'NOT confidence intervals' in svg
    assert svg.count('r="5"')==6
