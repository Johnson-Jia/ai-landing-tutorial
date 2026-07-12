"""会话记忆压缩:把长对话结构化压缩成 SESSION_MEMORY,保留关键信息。

结构(顺序即优先级):用户意图 > 用户纠正 > 错误与修正 > 活跃工作 > 已完成 > 待办 > 关键引用。
思路源自 Anthropic cookbooks session_memory_compaction(中文重写)。

无 ANTHROPIC_API_KEY 时只生成压缩 prompt(供 AI/人执行);有 key 时可调 LLM 真压缩。"""
from __future__ import annotations

import sys

# 结构章节(顺序即优先级,与下方一致:用户意图 > 用户纠正 > 错误与修正 > ...)
SESSION_SECTIONS = [
    "用户意图",
    "用户纠正",
    "错误与修正",
    "活跃工作",
    "已完成",
    "待办",
    "关键引用",
]


def build_compress_prompt(conversation: str) -> str:
    """生成结构化压缩 prompt(喂给 LLM 做压缩)。"""
    sections_block = "\n".join(f"- <{s}>...</{s}>" for s in SESSION_SECTIONS)
    return f"""把下面这段长对话压缩成一份【会话记忆】,供续接新会话用。

按以下结构输出(顺序即优先级,越靠前越重要,务必保留):
{sections_block}

优先级原则(关键):
- 用户纠正(用户修改/否决/明确反对过的)权重最高,必须保留原话,防止回退到旧行为
- 错误与修正 > 活跃工作 > 已完成(已完成的可最简)

待压缩对话:
---
{conversation}
---

只输出 <SESSION_MEMORY> 标签内的结构化结果,不要额外解释。"""


def compress(conversation: str, client=None) -> str:
    """有 anthropic client 则真调 LLM 压缩;无则返回 prompt 供后续执行。"""
    prompt = build_compress_prompt(conversation)
    if client is None:
        return prompt
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def main(argv: list[str] | None = None) -> int:
    # Windows GBK 终端中文乱码预防
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    import argparse
    from pathlib import Path

    p = argparse.ArgumentParser(description="会话记忆压缩 prompt 生成")
    p.add_argument("file", help="对话文本文件")
    p.add_argument("--compress", action="store_true", help="有 ANTHROPIC_API_KEY 时真调 LLM")
    args = p.parse_args(argv)
    conv = Path(args.file).read_text(encoding="utf-8")

    client = None
    if args.compress:
        import os

        if os.environ.get("ANTHROPIC_API_KEY"):
            import anthropic

            client = anthropic.Anthropic()

    print(compress(conv, client))
    return 0


if __name__ == "__main__":
    sys.exit(main())
