"""Ingestion 管线:文档 → 切分 → contextual embeddings → 入 zvec collection。

zvec schema:doc_id(STRING) + title(STRING) + content(STRING,FTS 索引) + embedding(FP32,HNSW 索引)。
"""
from __future__ import annotations

import os
from pathlib import Path

import zvec
from zvec import (
    CollectionOption,
    DataType,
    Doc,
    FieldSchema,
    FtsIndexParam,
    HnswIndexParam,
    VectorSchema,
)

from chunking import split_with_indices
from embed import Embedder

EMBED_DIM = 1024
FTS_TOKENIZER = "standard"  # 中文文档可换 jieba(zvec 支持)


def build_schema(dim: int = EMBED_DIM) -> zvec.CollectionSchema:
    return zvec.CollectionSchema(
        name="rag_service",
        fields=[
            FieldSchema("doc_id", DataType.STRING, nullable=False),
            FieldSchema("title", DataType.STRING, nullable=False),
            FieldSchema(
                "content",
                DataType.STRING,
                nullable=False,
                index_param=FtsIndexParam(
                    tokenizer_name=FTS_TOKENIZER, filters=["lowercase"]
                ),
            ),
        ],
        vectors=[
            VectorSchema(
                "embedding",
                DataType.VECTOR_FP32,
                dimension=dim,
                index_param=HnswIndexParam(),
            )
        ],
    )


def open_collection(db_path: str, dim: int = EMBED_DIM, read_only: bool = False):
    return zvec.create_and_open(
        path=db_path,
        schema=build_schema(dim),
        option=CollectionOption(read_only=read_only, enable_mmap=True),
    )


def contextualize_chunk(client, chunk: str, doc_title: str) -> str:
    """用 Claude 给 chunk 生成 1-2 句"在全文中的位置与含义"前缀,拼到 chunk 前。

    对应 cookbooks contextual-embeddings 的核心增强步骤。
    无 ANTHROPIC_API_KEY 时返回原文(降级,不增强)。"""
    if client is None:
        return chunk
    prompt = (
        f"<document>{doc_title}</document>\n"
        f"<chunk>{chunk[:500]}</chunk>\n"
        "用一句话(≤60字)简述这个 chunk 在文档中的位置和主题,直接输出简述,不要前缀:"
    )
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=80,
            messages=[{"role": "user", "content": prompt}],
        )
        ctx = resp.content[0].text.strip()
        return f"{ctx}\n\n{chunk}"
    except Exception:
        return chunk


def ingest_docs(
    coll,
    embedder: Embedder,
    docs: list[dict],
    db_dir: str,
    chunk_size: int = 500,
    overlap: int = 50,
    use_contextual: bool = True,
) -> int:
    """docs: [{"id","title","text"}]。切分、增强、embedding、入库。返回入库片段数。"""
    client = None
    if use_contextual and os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        client = anthropic.Anthropic()

    zvec_docs: list[Doc] = []
    for d in docs:
        chunks, _spans = split_with_indices(d["text"], chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            text_to_embed = (
                contextualize_chunk(client, chunk, d["title"]) if client else chunk
            )
            vec = embedder.embed(text_to_embed)
            zvec_docs.append(
                Doc(
                    id=f"{d['id']}__{i}",
                    fields={
                        "doc_id": d["id"],
                        "title": d["title"],
                        "content": chunk,
                    },
                    vectors={"embedding": vec},
                )
            )
    results = coll.insert(zvec_docs)
    if not all(r.ok() for r in results):
        failed = [r for r in results if not r.ok()]
        raise RuntimeError(f"{len(failed)} 个片段入库失败")
    return len(zvec_docs)


def load_docs_from_dir(docs_dir: str) -> list[dict]:
    """从目录加载 .txt/.md 文档,文件名(去后缀)作 title,文件 path 作 id。"""
    out = []
    for p in sorted(Path(docs_dir).glob("*")):
        if p.suffix.lower() not in {".txt", ".md"}:
            continue
        out.append(
            {"id": p.stem, "title": p.stem, "text": p.read_text(encoding="utf-8")}
        )
    return out
