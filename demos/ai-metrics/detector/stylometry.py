"""② 风格计量学复核（Stylometry）—— 用代码风格指纹复核 Co-authored-by，反伪造。

原理：每个作者有独特的代码风格指纹（字符级 n-gram 分布）；AI 生成的代码，
风格往往和作者本人不同。对被 Co-authored-by 标记的 AI 提交，算它和作者本人
风格画像的余弦相似度：

  - 相似度高（很像本人手写）→ Co-authored-by 可能是误标 → 降低置信度
  - 相似度低（不像本人）    → 确认是 AI 生成       → 维持高置信度

这样能挡住"VS Code Copilot 对手写代码也加 trailer"这类误标。

用 TF-IDF 加权（对应 ai-code-ratio 生产算法）：IDF 来自全局语料，降低
"所有代码都有的共性 n-gram"（如 def/return/空格）的权重，升高"作者特有"
n-gram 的权重——这样手写 vs AI 的风格差异才不会被 Python 语法共性淹没。
算法提炼自 ai-code-ratio/internal/detector/{ngram.go, stylometry.go}。
"""
import math


def extract_ngrams(text: str, n: int = 3) -> dict:
    """字符级 n-gram 计数。返回 {ngram: 出现次数}。"""
    counts = {}
    for i in range(len(text) - n + 1):
        g = text[i:i + n]
        counts[g] = counts.get(g, 0) + 1
    return counts


def tf_normalize(counts: dict) -> dict:
    """把 n-gram 计数归一化为词频向量（各分量之和为 1）。"""
    total = sum(counts.values())
    if total == 0:
        return {}
    return {g: c / total for g, c in counts.items()}


def build_idf(documents: list) -> dict:
    """从多个文档的 n-gram 计数，算每个 n-gram 的 IDF（逆文档频率）。

    共性 n-gram（出现在多数文档）→ IDF 低；特有 n-gram → IDF 高。
    用平滑公式 idf = log((N+1)/(df+1)) + 1，避免除零和负值。
    """
    N = len(documents)
    if N == 0:
        return {}
    df = {}
    for doc in documents:
        for g in doc:
            df[g] = df.get(g, 0) + 1
    return {g: math.log((N + 1) / (d + 1)) + 1 for g, d in df.items()}


def apply_tfidf(tf: dict, idf: dict) -> dict:
    """TF 向量 × IDF 权重 → TF-IDF 向量。"""
    return {g: v * idf.get(g, 0.0) for g, v in tf.items()}


def cosine_similarity(a: dict, b: dict) -> float:
    """两个向量的余弦相似度。完全相同=1.0，正交=0.0。"""
    dot = sum(a[k] * b[k] for k in a if k in b)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def confidence_from_similarity(sim: float) -> float:
    """相似度 → 置信度：越像本人（sim 高）→ 置信度越低（可能误标）。下限 0.1。"""
    return max(1.0 - sim, 0.1)


def build_profile(diff_texts: list, idf: dict, n: int = 3) -> dict:
    """从一组「干净提交」的 diff 文本 + 全局 IDF，建作者风格画像（TF-IDF 向量）。"""
    merged = "\n".join(diff_texts)
    if not merged.strip():
        return {}
    return apply_tfidf(tf_normalize(extract_ngrams(merged, n)), idf)


def validate(diff_text: str, profile: dict, idf: dict, n: int = 3):
    """复核一个 AI 提交：返回 (相似度, 置信度)。无画像或无 diff 返回 (None, None)。"""
    if not profile or not diff_text or not diff_text.strip():
        return None, None
    vec = apply_tfidf(tf_normalize(extract_ngrams(diff_text, n)), idf)
    sim = cosine_similarity(vec, profile)
    return sim, confidence_from_similarity(sim)
