#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
head -10 SKILL.md | grep -q "^name:" || { echo "缺 name"; exit 1; }
head -10 SKILL.md | grep -q "^description:" || { echo "缺 description"; exit 1; }
python scripts/compress.py --help >/dev/null || { echo "脚本跑不起来"; exit 1; }
python -m pytest tests -q >/dev/null || { echo "测试失败"; exit 1; }
echo "✅ session-memory 自检通过"
