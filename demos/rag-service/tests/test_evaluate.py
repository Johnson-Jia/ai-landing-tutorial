from evaluate_rag import recall_at_k, mrr, faithfulness_prompt


def test_recall_at_k_full_hit():
    retrieved = ["d1", "d2", "d3"]
    relevant = {"d1", "d2"}
    assert recall_at_k(retrieved, relevant, k=3) == 1.0


def test_recall_at_k_partial_hit():
    retrieved = ["d1", "d4", "d5"]
    relevant = {"d1", "d2"}
    # 命中 d1,relevant 共 2 个 → 0.5
    assert recall_at_k(retrieved, relevant, k=3) == 0.5


def test_recall_at_k_respects_k():
    retrieved = ["d4", "d1", "d2"]
    relevant = {"d1", "d2"}
    # k=1 时只看 d4 → 0
    assert recall_at_k(retrieved, relevant, k=1) == 0.0
    # k=3 时命中两个 → 1.0
    assert recall_at_k(retrieved, relevant, k=3) == 1.0


def test_mrr_first_relevant_at_rank1():
    assert mrr(["d1", "d2"], {"d1"}) == 1.0


def test_mrr_first_relevant_at_rank3():
    assert mrr(["d4", "d5", "d2", "d1"], {"d1", "d2"}) == 1 / 3


def test_mrr_no_relevant():
    assert mrr(["d4", "d5"], {"d1"}) == 0.0


def test_faithfulness_prompt_contains_answer_and_context():
    p = faithfulness_prompt(answer="苹果是水果", contexts=["苹果属于蔷薇科"])
    assert "苹果是水果" in p
    assert "苹果属于蔷薇科" in p
    assert "<faithfulness>" in p  # 要求结构化标签输出
