"""主入口 —— 确保示例数据 → 度量 AI 占比（含风格学）→ 提效同比 → Markdown 报告。

一键运行：python main.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # 让 detector 包、各模块可被 import
WORK = os.path.join(HERE, "workspace")   # 运行时产物单独放这里
REPO = os.path.join(WORK, "sample_repo")
RELEASES = os.path.join(WORK, "data", "sample_releases.xlsx")


def ensure_data():
    """示例数据不存在时，调 gen_data 生成（开箱即跑）。"""
    need = (not os.path.exists(os.path.join(REPO, ".git"))
            or not os.path.exists(RELEASES))
    if need:
        import gen_data
        gen_data.main()


def main():
    ensure_data()

    from git_ratio import measure
    from efficiency import parse_releases, analyze
    from report import render, render_html

    print("=== 1. AI 代码占比度量（含风格学反伪造）===")
    git_stats = measure(REPO)
    print(f"  提交占比 {git_stats['commit_ratio']:.1f}%（{git_stats['ai_commits']}/{git_stats['total_commits']}），"
          f"行数占比 {git_stats['line_ratio']:.1f}%")
    for email, a in git_stats["by_author"].items():
        print(f"  - {a['name']}：{a['ai']}/{a['total']} 提交为 AI")

    print("\n=== 2. 提效同比 ===")
    records = parse_releases(RELEASES)
    eff_stats = analyze(records)
    for y, s in eff_stats.items():
        print(f"  {y}：上线 {s['total']}（需求 {s['req']} / Bug {s['bug']}），{s['devs']} 人，人均 {s['per_capita']:.1f}")

    print("\n=== 3. 生成报告（Markdown + HTML）===")
    md = render(git_stats, eff_stats)
    out_md = os.path.join(WORK, "report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  Markdown：{out_md}")
    html = render_html(git_stats, eff_stats)
    out_html = os.path.join(WORK, "report.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML（ECharts 可视化）：{out_html}")


if __name__ == "__main__":
    main()
