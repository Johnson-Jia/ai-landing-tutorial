from analyze_slow_sql import analyze, Issue


def test_seq_scan_is_flagged():
    explain = "Seq Scan on public.users  (cost=0.00..154.00 rows=10000)"
    issues = analyze(explain)
    assert any(i.kind == "seq_scan" for i in issues)


def test_no_issue_on_index_scan():
    explain = "Index Scan using idx_user_id on users  (cost=0.29..8.31 rows=1)"
    assert analyze(explain) == []


def test_high_cost_flagged():
    explain = "Hash Join  (cost=1000.00..50000.00 rows=100)"
    issues = analyze(explain)
    assert any(i.kind == "high_cost" for i in issues)


def test_issue_has_advice():
    explain = "Seq Scan on orders  (cost=0.00..200.00 rows=5000)"
    issues = analyze(explain)
    assert len(issues) == 1
    assert "索引" in issues[0].advice or "index" in issues[0].advice.lower()
