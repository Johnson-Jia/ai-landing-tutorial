"""RAG 评估指标:recall@k / MRR / faithfulness(LLM-as-judge prompt)。

recall@k、MRR 是纯函数;faithfulness 需 LLM,这里只给 prompt 模板,
实际调用在 main.py 里按是否有 ANTHROPIC_API_KEY 决定。
"""
from __future__ import annotations


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """top-k 命中 relevant 的比例。"""
    if not relevant:
        return 0.0
    topk = retrieved[:k]
    hits = sum(1 for doc_id in topk if doc_id in relevant)
    return hits / len(relevant)


def mrr(retrieved: list[str], relevant: set[str]) -> float:
    """平均倒数排名:第一个命中 relevant 的位置倒数。"""
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def faithfulness_prompt(answer: str, contexts: list[str]) -> str:
    """构造 faithfulness 判定 prompt:回答是否忠实于检索上下文(防幻觉)。

    要求模型输出 <faithfulness>yes|no</faithfulness> + 理由。
    """
    context_block = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(contexts, 1))
    return f"""你在评估一段回答是否忠实于给定的检索上下文(防止幻觉)。

检索上下文:
{context_block}

回答:
{answer}

判定标准:回答中的每个事实性断言是否都能在上下文中找到支撑。
只回答一个标签 <faithfulness>yes</faithfulness> 或 <faithfulness>no</faithfulness>,
随后用一句话说明理由。"""
