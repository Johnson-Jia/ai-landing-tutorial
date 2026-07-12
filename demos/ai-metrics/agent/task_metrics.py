"""Agent 任务度量:成功率/平均耗时/重试。"""
from __future__ import annotations


def success_rate(tasks: list[dict]) -> float:
    ok = sum(1 for t in tasks if t.get("ok"))
    return ok / len(tasks) if tasks else 0.0


def avg_duration(tasks: list[dict]) -> float:
    ds = [t["duration_s"] for t in tasks if "duration_s" in t]
    return sum(ds) / len(ds) if ds else 0.0
