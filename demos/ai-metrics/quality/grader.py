"""输出质量评估:code-grading(精确/正则,最快)+ LLM-as-judge(grader prompt)。

核心哲学(源自 cookbooks building_evals):尽量把任务设计成可代码自动评分。
LLM-as-judge 用于无法代码评分的任务(开放性回答),输出 <correctness>yes|no</correctness>。"""
from __future__ import annotations

import re


def code_grade(
    response: str,
    expected: str,
    ignore_case: bool = False,
    strip: bool = True,
    regex: bool = False,
) -> bool:
    """code-grading:精确匹配或正则匹配。最快最可靠。

    默认 regex=False:字面量精确匹配(response == expected),含 ``.``/``-`` 的
    字面量(如 ``v1.2``/``2026-07-12``/IP)也按字面比较,避免启发式歧义。
    regex=True:expected 当作 pattern,按 :func:`re.fullmatch` 判定。
    """
    r = response
    e = expected
    if strip:
        r, e = r.strip(), e.strip()
    if ignore_case:
        r, e = r.lower(), e.lower()
    if regex:
        return re.fullmatch(e, r, re.IGNORECASE if ignore_case else 0) is not None
    return r == e


def llm_judge_prompt(response: str, criteria: str) -> str:
    """构造 LLM-as-judge prompt,要求输出 <correctness>yes|no</correctness>。"""
    return f"""你在评估一段 AI 输出的质量。

评估标准:{criteria}

待评估输出:
{response}

判定标准:输出是否满足上述标准(事实正确、无幻觉、无遗漏)。
只回答一个标签 <correctness>yes</correctness> 或 <correctness>no</correctness>,随后一句话理由。"""


def parse_judge_output(text: str) -> bool | None:
    """从 LLM 输出解析 <correctness>yes|no</correctness>。无标签返回 None。"""
    m = re.search(r"<correctness>\s*(yes|no)\s*</correctness>", text, re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower() == "yes"


def judge(response: str, criteria: str, client=None) -> bool | None:
    """有 anthropic client 则真调 LLM 判定;无则返回 None。"""
    if client is None:
        return None
    prompt = llm_judge_prompt(response, criteria)
    resp = client.messages.create(
        model="claude-haiku-4-5", max_tokens=128,
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_judge_output(resp.content[0].text)
