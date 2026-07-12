"""合成测试集模板(源自 cookbooks generate_test_cases 思路)。"""
from __future__ import annotations


def generate_testset_template(topic: str, cases: list[dict]) -> list[dict]:
    """cases: [{"input":..., "expected":..., "criteria":...}]。补 topic,返回标准化测试集。"""
    return [{"topic": topic, **c} for c in cases]
