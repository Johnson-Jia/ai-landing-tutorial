from agent.task_metrics import success_rate, avg_duration
from agent.token_usage import by_agent
from agent.tool_eval import tool_stats


def test_success_rate():
    tasks = [{"ok": True}, {"ok": True}, {"ok": False}]
    assert success_rate(tasks) == 2 / 3


def test_avg_duration():
    tasks = [{"duration_s": 10}, {"duration_s": 30}]
    assert avg_duration(tasks) == 20.0


def test_by_agent():
    usage = [{"agent": "researcher", "tokens": 5000}, {"agent": "coder", "tokens": 15000}]
    assert by_agent(usage) == {"researcher": 5000, "coder": 15000}


def test_tool_stats():
    calls = [
        {"tool": "search", "duration_s": 2, "feedback": "ok"},
        {"tool": "search", "duration_s": 4, "feedback": "slow"},
        {"tool": "run_sql", "duration_s": 10, "feedback": "ok"},
    ]
    stats = tool_stats(calls)
    assert stats["search"]["count"] == 2
    assert stats["search"]["avg_duration"] == 3.0
    assert stats["run_sql"]["count"] == 1
