#!/usr/bin/env bash
# agent-teams 自检:检查 Skill 包是否完整、可被 Claude Code 加载。
# 用法:bash verify.sh   退出码 0=通过,1=有缺失
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PKG_NAME="$(basename "$ROOT")"

pass=0; fail=0
ok()  { echo "  ✅ $1"; pass=$((pass+1)); }
err() { echo "  ❌ $1"; fail=$((fail+1)); }

echo "== agent-teams 自检 =="
echo "包根 : $ROOT"
echo "目录名: $PKG_NAME"
echo ""

# [1/3] 必需文件齐全
echo "[1/3] 文件齐全检查"
REQUIRED=(
  "SKILL.md"
  "manual.md"
  "README.md"
  "reference/orchestration.md"
  "reference/team-and-registry.md"
  "examples/project-registry.json"
  "examples/blueprint-example.md"
  "scripts/verify.sh"
)
for f in "${REQUIRED[@]}"; do
  if [ -f "$ROOT/$f" ]; then ok "$f"; else err "缺失: $f"; fi
done
echo ""

# [2/3] frontmatter 合法(提取首个 --- ... --- 块)
echo "[2/3] frontmatter 检查"
SKILL="$ROOT/SKILL.md"
if [ -f "$SKILL" ]; then
  fm="$(awk '/^---$/{c++; if(c==2) exit; if(c==1) next} c==1' "$SKILL")"
  if echo "$fm" | grep -q '^name:'; then
    name_val="$(echo "$fm" | sed -n 's/^name:[[:space:]]*//p' | tr -d "\"'")"
    if [ -n "$name_val" ]; then ok "frontmatter name = $name_val"; else err "frontmatter name 为空"; fi
    if [ "$name_val" = "$PKG_NAME" ]; then ok "name 与目录名一致"; else err "name($name_val) 与目录名($PKG_NAME) 不一致"; fi
  else
    err "frontmatter 缺少 name 字段"
  fi
  if echo "$fm" | grep -q '^description:'; then ok "frontmatter description 存在"; else err "frontmatter 缺少 description 字段"; fi
fi
echo ""

# [3/3] 注册表 JSON 可解析(node > python > python3,避开 Windows python3 Store stub)
echo "[3/3] JSON 解析检查"
REG="$ROOT/examples/project-registry.json"
if [ -f "$REG" ]; then
  parsed=0
  if node -e "JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'))" "$REG" >/dev/null 2>&1; then
    ok "project-registry.json 可解析(node)"; parsed=1
  elif python -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8'))" "$REG" >/dev/null 2>&1; then
    ok "project-registry.json 可解析(python)"; parsed=1
  elif python3 -c "import json,sys; json.load(open(sys.argv[1], encoding='utf-8'))" "$REG" >/dev/null 2>&1; then
    ok "project-registry.json 可解析(python3)"; parsed=1
  fi
  if [ "$parsed" -eq 0 ]; then
    err "project-registry.json 解析失败(需 node 或 python 验证)"
  fi
fi
echo ""

# 汇总
echo "== 结果 =="
echo "通过 $pass / 失败 $fail"
if [ "$fail" -gt 0 ]; then
  echo "❌ 自检未通过,请按上方提示补全。"
  exit 1
fi
echo "✅ 自检通过:包完整,可被 Claude Code 加载。"
exit 0
