"""缓存命中率分析:cache_read / input_tokens(缓存读取占新输入比例)。"""
from __future__ import annotations


def cache_ratio(usage: dict) -> float:
    """缓存命中率 = cache_read / input_tokens。无新输入返回 0。

    口径:每 1 个新输入 token 对应多少缓存命中。0.8 即 80% 新输入被缓存覆盖。
    (不含 output,因 prompt cache 只覆盖输入侧。)
    """
    inp = usage.get("input_tokens", 0)
    cr = usage.get("cache_read", 0)
    return cr / inp if inp else 0.0
