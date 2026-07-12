from cost.admin_api import load_usage
from cost.chargeback import attribute_by_workspace, to_csv
from cost.cache_efficiency import cache_ratio


def test_load_usage_falls_back_to_sample(tmp_path):
    import json
    sample = {"workspaces": [{"id": "ws1", "name": "团队A", "input_tokens": 1000, "cache_read": 800, "output_tokens": 200, "cost_usd": 1.5}]}
    p = tmp_path / "usage.json"
    p.write_text(json.dumps(sample), encoding="utf-8")
    usage = load_usage(sample_path=str(p))
    assert len(usage["workspaces"]) == 1


def test_attribute_by_workspace():
    usage = {"workspaces": [{"name": "A", "cost_usd": 10.0}, {"name": "B", "cost_usd": 30.0}]}
    attr = attribute_by_workspace(usage)
    assert attr == {"A": 10.0, "B": 30.0}


def test_to_csv_has_header_and_rows():
    attr = {"A": 10.0, "B": 30.0}
    csv = to_csv(attr)
    lines = csv.strip().split("\n")
    assert "workspace" in lines[0] and "cost_usd" in lines[0]
    assert any("A" in ln and "10" in ln for ln in lines[1:])


def test_cache_ratio():
    assert cache_ratio({"input_tokens": 1000, "cache_read": 800}) == 0.8
    assert cache_ratio({"input_tokens": 0, "cache_read": 0}) == 0.0
