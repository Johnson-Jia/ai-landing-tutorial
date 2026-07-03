"""③ 检测器注册表 —— 组合多个检测器，对每个 commit 给出最终判定。

流程（对应 ai-code-ratio detector.go + stylometry.go 的组合逻辑）：
  ① Co-authored-by 初筛：命中 AI 名单 → IsAI=true，置信度 1.0
  ② 风格计量学复核（仅对 IsAI=true）：算与作者画像的余弦相似度，校正置信度
     —— 相似度高（像本人）→ 降置信度（可能误标）；相似度低 → 确认 AI

profiles 是事先从每个作者的「干净提交」建好的风格画像：
  {author_email: TF 向量}
"""
from detector.coauthored import detect_coauthored
from detector.stylometry import validate


def detect_commit(commit: dict, profiles: dict, idf: dict) -> dict:
    """检测单个 commit。

    commit: {message, added_lines_text, author_email}
    profiles: {author_email: 风格画像}
    idf: 全局 n-gram IDF（风格学 TF-IDF 加权用）

    Returns: {is_ai, source, confidence, similarity}
    """
    # ① Co-authored-by 初筛
    is_ai, ai_name, conf = detect_coauthored(commit["message"])
    result = {"is_ai": is_ai, "source": None, "confidence": 0.0, "similarity": None}
    if not is_ai:
        return result

    result["source"] = f"co-authored-by:{ai_name}"
    result["confidence"] = conf  # 初筛置信度 1.0

    # ② 风格计量学复核（校正置信度，挡误标）
    profile = profiles.get(commit["author_email"])
    if profile:
        sim, conf2 = validate(commit["added_lines_text"], profile, idf)
        if sim is not None:
            result["similarity"] = sim
            result["confidence"] = conf2  # 用风格学校正后的置信度
            result["source"] += f" + stylometry(sim={sim:.2f},conf={conf2:.2f})"

    return result
