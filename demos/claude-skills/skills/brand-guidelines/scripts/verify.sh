#!/usr/bin/env bash
# brand-guidelines 自检:frontmatter 合法 + 脚本能跑 + 校验器对样例给出正确判断
set -e
cd "$(dirname "$0")/.."
# 1. frontmatter 有 name/description
head -10 SKILL.md | grep -q "^name:" || { echo "缺 name frontmatter"; exit 1; }
head -10 SKILL.md | grep -q "^description:" || { echo "缺 description"; exit 1; }
# 2. 脚本能跑(--help)
python scripts/validate_brand.py --help >/dev/null || { echo "validate_brand 跑不起来"; exit 1; }
python scripts/apply_brand.py --help >/dev/null || { echo "apply_brand 跑不起来"; exit 1; }
# 3. 校验器:合规样例退出 0,违规样例退出 1
python scripts/validate_brand.py examples/compliant.md >/dev/null || { echo "合规样例应通过"; exit 1; }
python scripts/validate_brand.py examples/violating.md >/dev/null && { echo "违规样例应报错"; exit 1; } || true
echo "✅ brand-guidelines 自检通过"
