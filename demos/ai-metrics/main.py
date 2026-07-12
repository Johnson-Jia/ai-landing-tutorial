"""主入口 —— 四维度度量：代码占比 / 输出质量 / API 成本 / Agent 效能。

一键运行（默认=原两维度，向后兼容）：python main.py
指定维度：python main.py --dim quality|cost|agent|all
"""
import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WORK = os.path.join(HERE, "workspace")
REPO = os.path.join(WORK, "sample_repo")
RELEASES = os.path.join(WORK, "data", "sample_releases.xlsx")


def ensure_data():
    need = (not os.path.exists(os.path.join(REPO, ".git")) or not os.path.exists(RELEASES))
    if need:
        import gen_data
        gen_data.main()


def run_code_dim():
    """[现有] AI 代码占比 + 提效同比（原 main 行为，保持向后兼容）。"""
    ensure_data()
    from git_ratio import measure
    from efficiency import parse_releases, analyze
    from report import render, render_html

    print("=== 1. AI 代码占比度量（含风格学反伪造）===")
    git_stats = measure(REPO)
    print(f"  提交占比 {git_stats['commit_ratio']:.1f}%，行数占比 {git_stats['line_ratio']:.1f}%")
    print("\n=== 2. 提效同比 ===")
    records = parse_releases(RELEASES)
    eff_stats = analyze(records)
    for y, s in eff_stats.items():
        print(f"  {y}：上线 {s['total']}（需求 {s['req']} / Bug {s['bug']}），人均 {s['per_capita']:.1f}")
    print("\n=== 3. 生成报告 ===")
    out_md = os.path.join(WORK, "report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(render(git_stats, eff_stats))
    out_html = os.path.join(WORK, "report.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(render_html(git_stats, eff_stats))
    print(f"  Markdown：{out_md}\n  HTML：{out_html}")


def run_quality_dim():
    from quality.run_eval import evaluate
    import json
    evalset_path = os.path.join(HERE, "quality", "sample_evalset.json")
    cases = json.loads(open(evalset_path, encoding="utf-8").read())
    # demo：用 expected 本身作 response（模拟"完美回答"），展示评估流程
    responses = [c["expected"] for c in cases]
    stats = evaluate(responses, cases)
    print(f"=== 输出质量评估 ===\n  样本 {stats['total']}，通过 {stats['passed']}，通过率 {stats['pass_rate']:.1%}")


def run_cost_dim():
    from cost.admin_api import load_usage
    from cost.chargeback import attribute_by_workspace, to_csv
    from cost.cache_efficiency import cache_ratio
    usage = load_usage(sample_path=os.path.join(HERE, "cost", "sample_usage.json"))
    attr = attribute_by_workspace(usage)
    print("=== API 成本可观测（FinOps）===")
    for name, cost in sorted(attr.items(), key=lambda x: -x[1]):
        ws = next(w for w in usage["workspaces"] if w["name"] == name)
        print(f"  {name}：${cost:.2f}（缓存命中率 {cache_ratio(ws):.1%}）")
    csv = to_csv(attr)
    out_csv = os.path.join(WORK, "chargeback.csv")
    with open(out_csv, "w", encoding="utf-8") as f:
        f.write(csv)
    print(f"  chargeback CSV：{out_csv}")


def run_agent_dim():
    from agent.task_metrics import success_rate, avg_duration
    from agent.token_usage import by_agent
    from agent.tool_eval import tool_stats
    tasks = [{"ok": True, "duration_s": 12}, {"ok": True, "duration_s": 18}, {"ok": False, "duration_s": 45}]
    usage = [{"agent": "researcher", "tokens": 5000}, {"agent": "coder", "tokens": 15000}]
    calls = [{"tool": "search", "duration_s": 2, "feedback": "ok"}, {"tool": "search", "duration_s": 6, "feedback": "slow"}]
    print("=== Agent 效能 ===")
    print(f"  任务成功率 {success_rate(tasks):.1%}，平均耗时 {avg_duration(tasks):.1f}s")
    print(f"  token 归因 {by_agent(usage)}")
    stats = tool_stats(calls)
    print(f"  工具统计：search(count={stats['search']['count']}, avg={stats['search']['avg_duration']}s)")


def main():
    p = argparse.ArgumentParser(description="AI 提效四维度度量")
    p.add_argument("--dim", choices=["code", "quality", "cost", "agent", "all"], default="code",
                   help="度量维度（默认 code=原两维度，向后兼容）")
    args = p.parse_args()

    if args.dim == "code":
        run_code_dim()
    elif args.dim == "quality":
        run_quality_dim()
    elif args.dim == "cost":
        run_cost_dim()
    elif args.dim == "agent":
        run_agent_dim()
    elif args.dim == "all":
        run_code_dim()
        print()
        run_quality_dim()
        print()
        run_cost_dim()
        print()
        run_agent_dim()


if __name__ == "__main__":
    main()
