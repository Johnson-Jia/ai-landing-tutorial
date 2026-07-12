"""token 按 agent 归因(哪个 agent 最烧 token)。"""
from __future__ import annotations


def by_agent(usage: list[dict]) -> dict[str, int]:
    """usage: [{"agent":..., "tokens":...}] → {agent: total_tokens}。"""
    out: dict[str, int] = {}
    for u in usage:
        out[u["agent"]] = out.get(u["agent"], 0) + u["tokens"]
    return out
