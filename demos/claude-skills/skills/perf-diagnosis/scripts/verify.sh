#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
head -10 SKILL.md | grep -q "^name:" || { echo "缺 name"; exit 1; }
head -10 SKILL.md | grep -q "^description:" || { echo "缺 description"; exit 1; }
python scripts/analyze_slow_sql.py --help >/dev/null || { echo "脚本跑不起来"; exit 1; }
python -m pytest tests -q >/dev/null || { echo "测试失败"; exit 1; }
# 实跑 examples 确认脚本对真实 EXPLAIN 有正确输出
python scripts/analyze_slow_sql.py examples/slow-sql.md | grep -q "seq_scan" || { echo "examples 未报 seq_scan"; exit 1; }
echo "✅ perf-diagnosis 自检通过"
