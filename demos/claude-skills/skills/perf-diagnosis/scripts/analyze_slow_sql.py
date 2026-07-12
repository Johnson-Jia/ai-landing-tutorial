"""慢 SQL 诊断:解析 EXPLAIN 输出,定位全表扫描/高成本/嵌套循环,给建议。

只读解析,绝不执行 SQL。"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

COST_RE = re.compile(r"\(cost=([\d.]+)\.\.([\d.]+)")
HIGH_COST_THRESHOLD = 10000.0  # 总成本上限(示例)


@dataclass
class Issue:
    kind: str  # seq_scan / high_cost / nested_loop
    detail: str
    advice: str


def analyze(explain: str) -> list[Issue]:
    """解析 EXPLAIN 文本,返回问题清单。"""
    issues: list[Issue] = []

    for line in explain.splitlines():
        if "Seq Scan" in line:
            issues.append(
                Issue(
                    kind="seq_scan",
                    detail=line.strip(),
                    advice="全表扫描:考虑在 WHERE/JOIN 列上加索引,或检查是否有索引未被命中(统计信息过期可 ANALYZE)。",
                )
            )
        if "Nested Loop" in line and "rows=1 " not in line:
            issues.append(
                Issue(
                    kind="nested_loop",
                    detail=line.strip(),
                    advice="嵌套循环在大数据集上是 O(n²):确认驱动表是小表,或改 Hash Join/Merge Join。",
                )
            )
        cost_match = COST_RE.search(line)
        if cost_match:
            total = float(cost_match.group(2))
            if total > HIGH_COST_THRESHOLD:
                issues.append(
                    Issue(
                        kind="high_cost",
                        detail=line.strip(),
                        advice=f"总成本 {total:.0f} 偏高:优先优化该节点的子操作(索引/过滤/分批)。",
                    )
                )

    return issues


def main(argv: list[str] | None = None) -> int:
    # Windows GBK 终端中文乱码预防
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    import argparse
    from pathlib import Path

    p = argparse.ArgumentParser(description="慢 SQL EXPLAIN 诊断")
    p.add_argument("file", help="EXPLAIN 输出文件")
    args = p.parse_args(argv)
    explain = Path(args.file).read_text(encoding="utf-8")
    issues = analyze(explain)
    if not issues:
        print("✅ 未发现明显性能问题(仍建议结合实际耗时判断)")
        return 0
    print(f"⚠️ 发现 {len(issues)} 个潜在问题:")
    for i in issues:
        print(f"  [{i.kind}] {i.detail}")
        print(f"      → {i.advice}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
