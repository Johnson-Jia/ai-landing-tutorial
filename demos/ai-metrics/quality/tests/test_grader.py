from quality.grader import code_grade, llm_judge_prompt, parse_judge_output


def test_code_grade_exact_match():
    assert code_grade("Paris", "Paris") is True
    assert code_grade("Paris", "London") is False


def test_code_grade_regex():
    assert code_grade("用户ID: 12345", r"用户ID: \d+") is True
    assert code_grade("无匹配", r"\d{10}") is False


def test_code_grade_normalized():
    assert code_grade("  paris ", "Paris", ignore_case=True, strip=True) is True


def test_llm_judge_prompt_contains_response_and_criteria():
    p = llm_judge_prompt(response="苹果是水果", criteria="事实正确,无幻觉")
    assert "苹果是水果" in p
    assert "事实正确" in p
    assert "<correctness>" in p


def test_parse_judge_output_yes():
    assert parse_judge_output("blah <correctness>yes</correctness> 理由") is True
    assert parse_judge_output("<correctness>no</correctness>") is False
    assert parse_judge_output("无标签") is None
