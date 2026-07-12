import json
from pathlib import Path

from embed import Embedder


def test_embedder_returns_vector_of_declared_dim():
    emb = Embedder(dim=8, allow_online=False, allow_local=False)
    v = emb.embed("hello world")
    assert isinstance(v, list)
    assert len(v) == 8


def test_embedder_deterministic_for_same_text_in_fallback():
    """兜底路径(无在线/无本地)对同一文本必须确定性,否则检索不可复现。"""
    emb = Embedder(dim=16, allow_online=False, allow_local=False)
    assert emb.embed("同一段话") == emb.embed("同一段话")


def test_embedder_different_text_different_vector_in_fallback():
    emb = Embedder(dim=16, allow_online=False, allow_local=False)
    assert emb.embed("苹果") != emb.embed("香蕉")


def test_embedder_uses_sample_vectors_when_provided(tmp_path):
    sample = {"苹果": [1.0] * 4, "香蕉": [0.0] * 4}
    p = tmp_path / "vectors.json"
    p.write_text(json.dumps(sample), encoding="utf-8")
    emb = Embedder(dim=4, allow_online=False, allow_local=False, sample_path=str(p))
    assert emb.embed("苹果") == [1.0] * 4
    # 未命中 sample 的走哈希兜底,仍返回 dim 长度向量
    assert len(emb.embed("橙子")) == 4


def test_embedder_reports_active_backend():
    emb = Embedder(dim=8, allow_online=False, allow_local=False)
    assert emb.backend in {"online", "local", "sample", "hash"}
