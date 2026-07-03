"""① Co-authored-by 初筛 —— 解析 commit message 的 trailer，匹配 AI 工具名单。

这是最直接的 AI 信号：AI 工具（Claude Code / Copilot / Cursor 等）默认会在
commit message 末尾埋 Co-authored-by trailer。命中名单 → 判为 AI，置信度 1.0。

缺陷：会被误标（如 VS Code Copilot 对人手写的代码也自动加 trailer），
所以需要 ② 风格计量学复核来挡误标。
"""
import re

# AI 工具名单（出现这些名字即认为是 AI 参与的提交）
AI_NAMES = ["claude", "copilot", "cursor", "chatgpt", "codeium", "gemini"]

# 匹配 "Co-authored-by: XXX <email>" 行
COAUTHORED_RE = re.compile(r"(?i)^co-authored-by:\s*(.+)$")


def detect_coauthored(message: str):
    """检测 commit message 是否含 AI 的 Co-authored-by。

    Returns:
        (is_ai, ai_name, confidence): 命中 AI 名单返回 (True, ai名, 1.0)；否则 (False, None, 0.0)
    """
    for line in message.splitlines():
        m = COAUTHORED_RE.match(line.strip())
        if not m:
            continue
        who = m.group(1).lower()
        for ai in AI_NAMES:
            if ai in who:
                return True, ai, 1.0
    return False, None, 0.0
