from compress import build_compress_prompt, SESSION_SECTIONS


def test_prompt_contains_all_sections():
    p = build_compress_prompt("用户:帮我改bug\nAI:已修复")
    for section in SESSION_SECTIONS:
        assert section in p


def test_prompt_contains_conversation():
    conv = "用户:苹果是水果吗\nAI:是的"
    p = build_compress_prompt(conv)
    assert "苹果是水果吗" in p


def test_sections_in_priority_order():
    # 用户纠正 > 错误 > 活跃 > 已完成(顺序反映优先级)
    p = build_compress_prompt("x")
    corrections_pos = p.find("用户纠正")
    completed_pos = p.find("已完成")
    assert 0 < corrections_pos < completed_pos


def test_prompt_has_output_instruction():
    p = build_compress_prompt("x")
    assert "SESSION_MEMORY" in p or "会话记忆" in p
