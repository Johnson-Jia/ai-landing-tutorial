#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
head -10 SKILL.md | grep -q "^name:" || { echo "缺 name"; exit 1; }
head -10 SKILL.md | grep -q "^description:" || { echo "缺 description"; exit 1; }
python scripts/compress.py --help >/dev/null || { echo "脚本跑不起来"; exit 1; }
python -m pytest tests -q >/dev/null || { echo "测试失败"; exit 1; }
# 实跑 examples 确认压缩脚本对真实对话有正确输出
python scripts/compress.py examples/before-after.md | grep -q "用户纠正" || { echo "examples 压缩结果缺关键词"; exit 1; }
echo "✅ session-memory 自检通过"
