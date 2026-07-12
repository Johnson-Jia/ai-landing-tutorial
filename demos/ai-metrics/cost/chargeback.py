"""按 workspace 归因成本 + CSV 导出(财务 chargeback)。"""
from __future__ import annotations


def attribute_by_workspace(usage: dict) -> dict[str, float]:
    """返回 {workspace_name: cost_usd}。"""
    return {w["name"]: w.get("cost_usd", 0.0) for w in usage.get("workspaces", [])}


def to_csv(attribution: dict[str, float]) -> str:
    """归因结果转 CSV(workspace, cost_usd)。"""
    lines = ["workspace,cost_usd"]
    for name, cost in sorted(attribution.items(), key=lambda x: -x[1]):
        lines.append(f"{name},{cost:.2f}")
    return "\n".join(lines) + "\n"
