"""三级递进检索(zvec):

L1 向量:  coll.query(Query(embedding, vector))
L2 +FTS:  coll.query(queries=[Query(content, fts), Query(embedding, vector)], reranker=RrfReRanker)
L3 +重排: L2 召回 → DefaultLocalReRanker(CrossEncoder)语义重排

对应 cookbooks contextual-embeddings 的三级递进(向量 → +BM25 → +CrossEncoder)。
"""
from __future__ import annotations

from zvec.model.param.query import Fts, Query


def retrieve_l1_vector(coll, query_vec: list[float], topk: int = 5):
    """L1 纯向量检索。"""
    return coll.query(
        Query(field_name="embedding", vector=query_vec), topk=topk
    )


def retrieve_l2_hybrid(
    coll, query_text: str, query_vec: list[float], topk: int = 5, rank_constant: int = 60
):
    """L2 向量 + FTS 混合,RRF 多路融合(对应 +BM25)。"""
    from zvec.extension.multi_vector_reranker import RrfReRanker

    reranker = RrfReRanker(rank_constant=rank_constant)
    return coll.query(
        queries=[
            Query(field_name="content", fts=Fts(match_string=query_text)),
            Query(field_name="embedding", vector=query_vec),
        ],
        topk=topk,
        reranker=reranker,
    )


def retrieve_l3_rerank(
    coll,
    query_text: str,
    query_vec: list[float],
    topk: int = 5,
    allow_model: bool = True,
    model_name: str = "BAAI/bge-reranker-base",
):
    """L3 混合召回 + CrossEncoder 语义重排(对应 +rerank)。

    allow_model=False 或无网络/模型时,回退到 L2。
    """
    if not allow_model:
        return retrieve_l2_hybrid(coll, query_text, query_vec, topk=topk)
    try:
        from zvec.extension.sentence_transformer_rerank_function import (
            DefaultLocalReRanker,
        )

        reranker = DefaultLocalReRanker(
            query=query_text,
            rerank_field="content",
            model_name=model_name,
            model_source="modelscope",  # 国内推荐
        )
        return coll.query(
            queries=[
                Query(field_name="content", fts=Fts(match_string=query_text)),
                Query(field_name="embedding", vector=query_vec),
            ],
            topk=topk,
            reranker=reranker,
        )
    except Exception:
        # 模型下载失败/无网络 → 回退 L2
        return retrieve_l2_hybrid(coll, query_text, query_vec, topk=topk)


def doc_ids(results) -> list[str]:
    """从检索结果提取 doc_id 字段(去重保序)。"""
    seen, ids = set(), []
    for d in results:
        did = d.fields.get("doc_id") if hasattr(d, "fields") else None
        if did and did not in seen:
            seen.add(did)
            ids.append(did)
    return ids
