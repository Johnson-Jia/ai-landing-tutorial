import gc
import os
import shutil
import tempfile

import pytest
from embed import Embedder
from ingest import open_collection, ingest_docs
from retrieve import retrieve_l1_vector, retrieve_l2_hybrid, retrieve_l3_rerank


@pytest.fixture
def populated_collection():
    """Windows 安全 fixture:mkdtemp + del coll/gc.collect + rmtree(ignore_errors)。

    zvec(RocksDB)collection 在 GC 前持有 LOCK 文件句柄,
    不能用 with TemporaryDirectory()(teardown 会 WinError 32)。"""
    emb = Embedder(dim=32, allow_online=False, allow_local=False)
    docs = [
        {"id": "vec", "title": "向量检索", "text": "向量数据库支持语义相似度检索"},
        {"id": "fts", "title": "全文检索", "text": "倒排索引实现关键词全文检索"},
        {"id": "mix", "title": "混合检索", "text": "向量与全文融合的混合检索效果更好"},
    ]
    td = tempfile.mkdtemp()
    try:
        coll = open_collection(os.path.join(td, "db"), dim=32)
        ingest_docs(coll, emb, docs, td, use_contextual=False)
        yield coll, emb
        del coll
        gc.collect()
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_l1_returns_at_most_topk(populated_collection):
    coll, emb = populated_collection
    qv = emb.embed("语义检索")
    res = retrieve_l1_vector(coll, qv, topk=2)
    assert 0 < len(res) <= 2
    assert all(hasattr(d, "score") for d in res)


def test_l2_hybrid_requires_two_signals(populated_collection):
    coll, emb = populated_collection
    res = retrieve_l2_hybrid(coll, query_text="检索", query_vec=emb.embed("检索"), topk=3)
    assert len(res) > 0


def test_l3_rerank_falls_back_when_no_model(populated_collection):
    """无 CrossEncoder 模型时,L3 应回退到 L2,不抛异常。"""
    coll, emb = populated_collection
    res = retrieve_l3_rerank(
        coll, query_text="检索", query_vec=emb.embed("检索"), topk=3, allow_model=False
    )
    assert len(res) > 0
