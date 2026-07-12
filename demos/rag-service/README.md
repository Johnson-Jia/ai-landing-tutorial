# RAG 端到端服务 Demo(基于 zvec)

> 教程 stage3「基础设施」配套 demo · 补全 RAG 从切分到评估的完整链路 · 复现 [cookbooks contextual-embeddings](https://github.com/anthropics/anthropic-cookbook) 三级递进优化。

## 这是什么

一个**生产级、可端到端运行**的最小 RAG 服务:文档切分 → contextual embeddings → 入库(zvec)→ 三级递进检索 → 评估出表。补 stage3「只有检索侧代码片段」的留白。

## 三级递进(核心)

| 级别 | 策略 | 对应 cookbooks | 解决什么 |
|---|---|---|---|
| L1 | 纯向量 | baseline RAG | 语义相似 |
| L2 | +FTS 混合(RRF 融合) | +BM25 | 关键词召回补充（对应官方 context+BM25 的 **49%** 降幅：5.7%→2.9%）|
| L3 | +CrossEncoder 重排 | +rerank | 精排，叠加后累计降 **67%** 检索失败率（官方：context+BM25 降 49%、再 +rerank 降 67%，5.7%→1.9%）|

## 快速开始

```bash
pip install -r requirements.txt
python main.py                 # 走兜底(无 key 也能看三级流程)
python main.py --no-rerank-model  # L3 不下模型,回退 L2
```

有 `DASHSCOPE_API_KEY` / `ANTHROPIC_API_KEY` 时自动启用在线 embedding + contextual embeddings,数值反映真实质量。

> Windows cmd 中文乱码时,设 `PYTHONIOENCODING=utf-8` 再跑。

## embedding 三层降级

| 后端 | 触发条件 | 用途 |
|---|---|---|
| online | 有 API key | 生产 |
| local | 装了 sentence_transformers + 模型 | 离线生产 |
| sample | workspace/vectors.json 命中 | 教学演示 |
| hash | 以上都不可用 | 流程演示(语义无关) |

## 目录

- `chunking.py` 切分(纯函数)
- `embed.py` 三层降级 embedding
- `ingest.py` 切分 + contextual embeddings + 入库
- `retrieve.py` 三级递进检索
- `evaluate_rag.py` recall@k / MRR / faithfulness
- `main.py` 一键演示
- `tests/` 单元 + 集成测试
- `workspace/docs/` sample 文档 · `workspace/evalset.json` 评估集

## 测试

```bash
cd demos/rag-service && python -m pytest tests -v
```

## 关键概念

- **contextual embeddings**:给每个 chunk 生成"在全文中的位置与含义"简述再 embedding——cookbooks 实测的最大单步提升。
- **RRF 融合**:多路召回结果按排名倒数加权合并,无需对齐分数。
- **CrossEncoder**:query-doc 联合编码精排,比 bi-encoder 更准但更慢,只对 top-k 用。

## 与教程的关系

stage3 §2「业务知识 RAG 服务」的端到端实物。stage5「度量」的检索质量评估(recall@k/MRR)也复用本 demo 的 `evaluate_rag.py`。

## 借鉴声明

三级递进与 contextual embeddings 思路源自 Anthropic cookbooks `capabilities/contextual-embeddings`(本 demo 为中文重写 + zvec 实现)。zvec 为阿里巴巴开源(Apache-2.0)。
