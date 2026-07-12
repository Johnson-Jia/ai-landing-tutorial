"""一键演示:ingest → 三级检索 → 评估出对比表。

无 ANTHROPIC_API_KEY / 无本地模型时全程走兜底,仍输出完整对比表(结果为流程演示)。
有 key + 模型时反映真实检索质量。
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from embed import Embedder
from evaluate_rag import recall_at_k, mrr
from ingest import ingest_docs, load_docs_from_dir, open_collection
from retrieve import retrieve_l1_vector, retrieve_l2_hybrid, retrieve_l3_rerank, doc_ids

WORKSPACE = Path(__file__).parent / "workspace"
DOCS_DIR = WORKSPACE / "docs"
EVALSET = WORKSPACE / "evalset.json"
DB_DIR = WORKSPACE / "zvec_db"
VECTORS = WORKSPACE / "vectors.json"
DIM = 1024
TOPK = 10


def main(use_contextual=True, use_rerank_model=True):
    print("=" * 60)
    print("RAG 三级递进演示(基于 zvec)")
    print("=" * 60)

    embedder = Embedder(
        dim=DIM,
        sample_path=str(VECTORS) if VECTORS.exists() else None,
    )
    print(f"[embedding 后端] {embedder.backend}")

    # 1. ingest
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR, ignore_errors=True)  # Windows LOCK 安全
    coll = open_collection(str(DB_DIR), dim=DIM)
    docs = load_docs_from_dir(str(DOCS_DIR))
    if not docs:
        print(f"[警告] {DOCS_DIR} 下无 .txt/.md 文档,请先准备 sample 文档")
        return
    n = ingest_docs(coll, embedder, docs, str(DB_DIR), use_contextual=use_contextual)
    print(f"[ingest] {len(docs)} 篇文档 → {n} 个片段入库")

    # 2. 评估
    evalset = json.loads(EVALSET.read_text(encoding="utf-8"))
    levels = {
        "L1 向量": lambda q, qv: retrieve_l1_vector(coll, qv, topk=TOPK),
        "L2 +FTS混合": lambda q, qv: retrieve_l2_hybrid(coll, q, qv, topk=TOPK),
        "L3 +重排": lambda q, qv: retrieve_l3_rerank(
            coll, q, qv, topk=TOPK, allow_model=use_rerank_model
        ),
    }
    agg = {name: {"recall": [], "mrr": []} for name in levels}

    for item in evalset:
        q, relevant = item["question"], set(item["relevant_ids"])
        qv = embedder.embed(q)
        for name, fn in levels.items():
            ids = doc_ids(fn(q, qv))
            agg[name]["recall"].append(recall_at_k(ids, relevant, TOPK))
            agg[name]["mrr"].append(mrr(ids, relevant))

    # 3. 打印对比表
    print("\n" + "=" * 60)
    print(f"{'检索策略':<16}{'recall@10':>12}{'MRR':>10}")
    print("-" * 60)
    for name in levels:
        r = sum(agg[name]["recall"]) / len(agg[name]["recall"])
        m = sum(agg[name]["mrr"]) / len(agg[name]["mrr"])
        print(f"{name:<16}{r:>12.2%}{m:>10.3f}")
    print("=" * 60)
    print("注:无 key/模型时走兜底,数值仅演示流程;有 key+模型时反映真实质量。")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--no-contextual", action="store_true", help="关闭 contextual embeddings(对比用)")
    p.add_argument("--no-rerank-model", action="store_true", help="L3 不下载 cross-encoder,回退 L2")
    args = p.parse_args()
    main(
        use_contextual=not args.no_contextual,
        use_rerank_model=not args.no_rerank_model,
    )
