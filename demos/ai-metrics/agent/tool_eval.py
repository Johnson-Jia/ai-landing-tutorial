"""工具反向评估(源自 cookbooks tool_evaluation):评估"工具设计得好不好"。

统计每工具调用次数/平均耗时/Agent feedback——工具优化依据。"""
from __future__ import annotations


def tool_stats(calls: list[dict]) -> dict[str, dict]:
    """calls: [{"tool", "duration_s", "feedback"}] → {tool: {count, avg_duration, feedbacks}}。"""
    agg: dict[str, list] = {}
    for c in calls:
        agg.setdefault(c["tool"], []).append(c)
    return {
        tool: {
            "count": len(cs),
            "avg_duration": sum(c["duration_s"] for c in cs) / len(cs),
            "feedbacks": [c.get("feedback", "") for c in cs],
        }
        for tool, cs in agg.items()
    }
