from urllib.parse import parse_qs, urlparse
import pytest
from multiyear_energy_validation import eia_api


def test_query_filters_and_sort():
    url = eia_api.build_request_url(api_key="TEST", respondent="CISO",
        start="2021-01-01T00", end="2021-12-31T23")
    q = parse_qs(urlparse(url).query)
    assert q["facets[type][]"] == ["D"]
    assert q["facets[respondent][]"] == ["CISO"]
    assert q["sort[0][column]"] == ["period"]
    assert q["length"] == ["5000"]


def test_paginated_candidate_data(monkeypatch):
    calls = []
    def fake_fetch(url, **kwargs):
        q = parse_qs(urlparse(url).query)
        calls.append(int(q["offset"][0]))
        return {"total": "3", "data": ([{"period": "a"}, {"period": "b"}]
            if len(calls) == 1 else [{"period": "c"}])}
    monkeypatch.setattr(eia_api, "fetch_json", fake_fetch)
    rows = eia_api.fetch_candidate_pages(api_key="TEST", respondent="CISO",
        start="2021", end="2021", max_rows=10)
    assert len(rows) == 3 and calls == [0, 2]


def test_reject_truncated_scope(monkeypatch):
    monkeypatch.setattr(eia_api, "fetch_json",
        lambda url: {"total": "20001", "data": []})
    with pytest.raises(ValueError, match="max_rows"):
        eia_api.fetch_candidate_pages(api_key="TEST", respondent="CISO",
            start="2021", end="2021")
