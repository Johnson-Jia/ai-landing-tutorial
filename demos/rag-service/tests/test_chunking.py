from chunking import split_text


def test_split_short_text_returns_single_chunk():
    chunks = split_text("短文本", chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == "短文本"


def test_split_respects_chunk_size():
    text = "字" * 250
    chunks = split_text(text, chunk_size=100, overlap=20)
    assert all(len(c) <= 100 for c in chunks)
    assert len(chunks) >= 3  # 250 字按 100 切、20 重叠至少 3 段


def test_split_overlap_creates_shared_content():
    text = "abcdefghij" * 20  # 200 字符
    chunks = split_text(text, chunk_size=100, overlap=20)
    # 相邻两段应有 overlap 个字符的公共内容
    assert chunks[0][-20:] == chunks[1][:20]


def test_split_empty_text_returns_empty_list():
    assert split_text("", chunk_size=100, overlap=20) == []


def test_split_yields_indices_for_traceability():
    from chunking import split_with_indices
    text = "x" * 250
    chunks, spans = split_with_indices(text, chunk_size=100, overlap=20)
    assert len(chunks) == len(spans)
    assert spans[0] == (0, 100)
    # 重叠:第二段起点 = 100 - 20
    assert spans[1] == (80, 180)
