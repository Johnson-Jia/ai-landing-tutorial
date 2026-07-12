"""跑评估集,算准确率/通过率。"""
from __future__ import annotations

from quality.grader import code_grade, judge


def evaluate(responses: list[str], cases: list[dict], use_llm: bool = False, client=None) -> dict:
    """对每个 case 用 code_grade(有 expected)或 judge(有 criteria)评分。"""
    passed = 0
    for resp, case in zip(responses, cases):
        ok = False
        if case.get("expected"):
            ok = code_grade(resp, case["expected"], ignore_case=True, strip=True)
        elif use_llm and case.get("criteria"):
            ok = judge(resp, case["criteria"], client=client) is True
        if ok:
            passed += 1
    total = len(cases)
    return {"total": total, "passed": passed, "pass_rate": passed / total if total else 0.0}
