"""AI 代码占比度量 —— 解析 git 仓库，用三层检测器识别 AI 提交，统计占比。

流程（对应 ai-code-ratio 的 git + analyzer + detector）：
  1. git log -p 解析所有提交（hash / 作者 / message / added lines）
  2. 用作者的「干净提交」（无 Co-authored-by）建风格画像
  3. 三层检测器检测每个提交（Co-authored-by 初筛 + 风格学复核）
  4. 统计：提交占比 + 行数占比（双口径）+ 作者明细
"""
import subprocess
from detector.registry import detect_commit
from detector.stylometry import build_profile, build_idf, extract_ngrams
from detector.coauthored import detect_coauthored


def _run_out(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout


def parse_commits(repo):
    """解析 git log -p，返回 commit 列表。每个 commit 含 message、added_lines。"""
    out = _run_out(["git", "log", "--no-merges", "-p",
                    "--format=__COMMIT__%H%n__EMAIL__%ae%n__NAME__%an%n__BODY__%B"], repo)
    commits = []
    for block in out.split("__COMMIT__")[1:]:
        lines = block.split("\n")
        commit = {"hash": lines[0].strip(), "author_email": "", "author_name": "",
                  "message": "", "added_lines": [], "added_lines_text": ""}
        i = 1
        body_start = -1
        while i < len(lines):
            ln = lines[i]
            if ln.startswith("__EMAIL__"):
                commit["author_email"] = ln[len("__EMAIL__"):]
            elif ln.startswith("__NAME__"):
                commit["author_name"] = ln[len("__NAME__"):]
            elif ln.startswith("__BODY__"):
                body_start = i + 1
                break
            i += 1
        added = []
        if body_start >= 0:
            j = body_start
            body = []
            while j < len(lines) and not lines[j].startswith("diff --git"):
                body.append(lines[j])
                j += 1
            commit["message"] = "\n".join(body).strip()
            while j < len(lines):  # diff 区：提取新增行（+ 开头，排除 +++ 文件名行）
                ln = lines[j]
                if ln.startswith("+") and not ln.startswith("+++"):
                    added.append(ln[1:])
                j += 1
        commit["added_lines"] = added
        commit["added_lines_text"] = "\n".join(added)
        commits.append(commit)
    return commits


def measure(repo):
    """度量一个 git 仓库的 AI 代码占比。"""
    commits = parse_commits(repo)

    # 1. 算全局 IDF（所有提交的 n-gram 文档频率）—— TF-IDF 加权用，降低共性 n-gram 权重
    idf = build_idf([extract_ngrams(c["added_lines_text"]) for c in commits])

    # 2. 用每个作者的「干净提交」（无 Co-authored-by）建风格画像（TF-IDF 向量）
    clean_by_author = {}
    for c in commits:
        is_ai, _, _ = detect_coauthored(c["message"])
        if not is_ai:
            clean_by_author.setdefault(c["author_email"], []).append(c["added_lines_text"])
    profiles = {email: build_profile(texts, idf) for email, texts in clean_by_author.items()}

    # 3. 三层检测器检测每个提交
    for c in commits:
        c["detect"] = detect_commit(
            {"message": c["message"], "added_lines_text": c["added_lines_text"],
             "author_email": c["author_email"]},
            profiles, idf,
        )

    # 3. 统计
    total = len(commits)
    ai_commits = [c for c in commits if c["detect"]["is_ai"]]
    total_added = sum(len(c["added_lines"]) for c in commits)
    ai_added = sum(len(c["added_lines"]) for c in ai_commits)

    by_author = {}
    for c in commits:
        a = by_author.setdefault(c["author_email"],
                                 {"name": c["author_name"], "total": 0, "ai": 0, "added": 0, "ai_added": 0})
        a["total"] += 1
        a["added"] += len(c["added_lines"])
        if c["detect"]["is_ai"]:
            a["ai"] += 1
            a["ai_added"] += len(c["added_lines"])

    return {
        "commits": commits,
        "total_commits": total,
        "ai_commits": len(ai_commits),
        "commit_ratio": (len(ai_commits) / total * 100) if total else 0,
        "total_added": total_added,
        "ai_added": ai_added,
        "line_ratio": (ai_added / total_added * 100) if total_added else 0,
        "by_author": by_author,
    }
