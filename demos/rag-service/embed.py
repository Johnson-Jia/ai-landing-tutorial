"""统一 embedding 封装:三层降级,对外只暴露 embed(text)->list[float]。

降级优先级:
1. 在线(DashScope key)→ QwenDenseEmbedding(zvec 扩展)
2. 本地 sentence_transformers(BAAI/bge-m3 等)
3. sample 预计算 JSON(workspace/vectors.json)
4. 哈希兜底(确定性、无依赖、语义无关——仅用于演示检索流程跑通)

教学含义:生产用 1/2;课堂教学或 CI 用 3/4。

注:在线分支只认 DASHSCOPE_API_KEY(Qwen/DashScope 鉴权);ANTHROPIC_API_KEY
无法鉴权 DashScope,曾导致 401 被静默吞、backend 误标 "online" 实际走 hash。
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np


class Embedder:
    def __init__(
        self,
        dim: int = 1024,
        allow_online: bool = True,
        allow_local: bool = True,
        sample_path: str | None = None,
        local_model: str = "BAAI/bge-m3",
    ) -> None:
        self.dim = dim
        self.backend: str = "hash"
        self._impl = None
        self._sample: dict[str, list[float]] = {}

        # 1. 在线(仅认 DashScope key;Anthropic key 无法鉴权 DashScope/Qwen)
        if allow_online:
            key = os.environ.get("DASHSCOPE_API_KEY")
            if key:
                try:
                    # 签名参照 zvec.extension.qwen_embedding_function 文档:
                    # QwenDenseEmbedding(dimension=..., api_key=..., model=...)
                    from zvec.extension.qwen_embedding_function import QwenDenseEmbedding

                    self._impl = QwenDenseEmbedding(dimension=dim, api_key=key)
                    self.backend = "online"
                except Exception:
                    self._impl = None

        # 2. 本地 sentence_transformers
        if self._impl is None and allow_local:
            try:
                from zvec.extension.sentence_transformer_embedding_function import (
                    SentenceTransformerDenseEmbedding,
                )

                # 类名按 zvec 实际导出调整;若该名不存在,回退直接用 sentence_transformers
                self._impl = _LocalSentenceTransformer(local_model, dim)
                self.backend = "local"
            except Exception:
                self._impl = None

        # 3. sample 预计算
        if self._impl is None and sample_path and Path(sample_path).exists():
            self._sample = json.loads(Path(sample_path).read_text(encoding="utf-8"))
            self.backend = "sample"

        # 4. 哈希兜底(self.backend 保持 "hash")

    def embed(self, text: str) -> list[float]:
        if self._impl is not None:
            try:
                v = self._impl.embed(text)
                if isinstance(v, list) and len(v) == self.dim:
                    return v
            except Exception:
                pass  # 在线/本地失败,降级
        if text in self._sample:
            return self._sample[text]
        return self._hash_vec(text)

    def _hash_vec(self, text: str) -> list[float]:
        """确定性哈希到单位向量。语义无关,仅供流程演示。"""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        repeats = (self.dim // 32) + 1
        # digest 是 bytes(uint8 每元素 1 字节),只需切到 dim 长度;原 dim*4 是死切片
        buf = (digest * repeats)[: self.dim]
        v = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
        norm = np.linalg.norm(v)
        return (v / (norm + 1e-9)).tolist()


class _LocalSentenceTransformer:
    """sentence_transformers 直连封装(不依赖 zvec 扩展确切类名时的兜底)。"""

    def __init__(self, model_name: str, dim: int) -> None:
        from sentence_transformers import SentenceTransformer  # type: ignore

        self._model = SentenceTransformer(model_name)
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        v = self._model.encode(text, normalize_embeddings=True)
        return v.tolist()
