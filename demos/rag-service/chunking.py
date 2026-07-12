"""文本切分:固定 size + overlap,返回片段(可选带原文区间)。

纯函数,无外部依赖。"""
from __future__ import annotations


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """按 chunk_size 切分,相邻片段重叠 overlap 个字符。

    Args:
        text: 原文。
        chunk_size: 每段最大字符数。
        overlap: 相邻段重叠字符数(必须 < chunk_size)。

    Returns:
        切分后的文本片段列表;空文本返回 []。
    """
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError(f"overlap({overlap}) 必须小于 chunk_size({chunk_size})")
    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size]
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
    return chunks


def split_with_indices(
    text: str, chunk_size: int = 500, overlap: int = 50
) -> tuple[list[str], list[tuple[int, int]]]:
    """切分并返回每段在原文中的 (start, end) 区间,便于溯源。"""
    if not text:
        return [], []
    if overlap >= chunk_size:
        raise ValueError(f"overlap({overlap}) 必须小于 chunk_size({chunk_size})")
    step = chunk_size - overlap
    chunks, spans = [], []
    for start in range(0, len(text), step):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        spans.append((start, end))
        if end >= len(text):
            break
    return chunks, spans
