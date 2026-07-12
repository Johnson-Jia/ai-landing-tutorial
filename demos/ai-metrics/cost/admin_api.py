"""Anthropic Admin API 封装:usage/cost 按 workspace。

无 ANTHROPIC_API_KEY 或无 Admin 权限时用 sample JSON 兜底(演示归因报表流程)。
源自 cookbooks observability/usage_cost_api。"""
from __future__ import annotations

import json
import os
from pathlib import Path


def load_usage(sample_path: str | None = None) -> dict:
    """有 Admin API key 时真调;否则用 sample JSON。返回 {workspaces: [...]}。"""
    key = os.environ.get("ANTHROPIC_ADMIN_API_KEY")
    if key:
        try:
            return _fetch_from_admin_api(key)
        except NotImplementedError:
            # 占位实现:明示用户当前用的是 sample,而非真 API
            print("[cost] Admin API 未接入(占位),用 sample 演示归因流程")
        except Exception as e:  # 其他异常仍降级,但提示
            print(f"[cost] Admin API 调用失败({e!r}),降级用 sample")
    if sample_path and Path(sample_path).exists():
        return json.loads(Path(sample_path).read_text(encoding="utf-8"))
    # 最兜底:内置极小 sample
    return {"workspaces": [{"id": "ws0", "name": "示例团队", "input_tokens": 1000, "cache_read": 600, "output_tokens": 200, "cost_usd": 1.2}]}


def _fetch_from_admin_api(key: str) -> dict:
    """真调 Admin API(需企业账号 + admin key)。占位,实际用 anthropic SDK 的 admin 接口。"""
    raise NotImplementedError("Admin API 接入待实现(本 demo 用 sample 演示归因流程)")
