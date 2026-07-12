from validate_brand import validate, BRAND_COLORS, BRAND_FONTS


def test_compliant_text_has_no_violations():
    text = '<div style="color:#1A56DB;font-family:Inter">合规</div>'
    assert validate(text) == []


def test_off_brand_color_is_flagged():
    text = '<div style="color:#8B5CF6">紫色不在规范</div>'
    violations = validate(text)
    assert len(violations) == 1
    assert "8B5CF6" in violations[0]


def test_off_brand_font_is_flagged():
    # 真实 CSS 常用引号包裹含空格的字体名
    text = "<div style=\"font-family:'Comic Sans MS'\">违规字体</div>"
    violations = validate(text)
    assert any("Comic Sans MS" in v for v in violations)


def test_quoted_font_extracted():
    # 引号包裹的字体名应被正确提取(不被吞成空)
    text = "<div style=\"font-family:'PingFang SC'\">合规</div>"
    assert validate(text) == []  # PingFang SC 在白名单
    text2 = "<div style=\"font-family:'Comic Sans MS'\">违规</div>"
    assert any("Comic Sans MS" in v for v in validate(text2))


def test_brand_colors_whitelist_includes_primary():
    assert "#1A56DB" in BRAND_COLORS
    assert "#16A34A" in BRAND_COLORS


def test_case_insensitive_color_match():
    text = '<div style="color:#1a56db">小写也合规</div>'
    assert validate(text) == []
