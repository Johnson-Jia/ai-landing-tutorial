"""品牌合规校验器:扫描文本中的颜色(hex)与字体,对比白名单,输出违规。

只校验不修改。退出码:0 合规,1 有违规。"""
from __future__ import annotations

import re
import sys

# 品牌规范(示例:科技蓝主题;实际项目替换为自己的品牌色卡)
BRAND_COLORS = {"#1A56DB", "#16A34A", "#F59E0B", "#0F172A", "#FFFFFF"}
BRAND_FONTS = {"PingFang SC", "Inter", "SF Mono", "Microsoft YaHei"}

HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;\"'\n]+)", re.IGNORECASE)


def validate(text: str) -> list[str]:
    """返回违规清单(每条一句)。空列表表示合规。"""
    violations: list[str] = []

    for m in HEX_RE.findall(text):
        if m.upper() not in {c.upper() for c in BRAND_COLORS}:
            violations.append(f"颜色 {m} 不在品牌色卡 {sorted(BRAND_COLORS)}")

    for m in FONT_RE.findall(text):
        # 取第一个字体名(逗号分隔)
        first = m.split(",")[0].strip().strip("'\"")
        if first and first not in BRAND_FONTS:
            violations.append(f"字体 '{first}' 不在品牌字体 {sorted(BRAND_FONTS)}")

    return violations


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys as _sys

    # Windows 控制台默认 GBK,这里强制 stdout 用 utf-8,避免 emoji 报错
    try:
        _sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    p = argparse.ArgumentParser(description="品牌合规校验")
    p.add_argument("file", help="待校验的 .html/.md/.css 文件路径")
    args = p.parse_args(argv)
    from pathlib import Path

    text = Path(args.file).read_text(encoding="utf-8")
    violations = validate(text)
    if not violations:
        print("✅ 品牌合规")
        return 0
    print(f"❌ 发现 {len(violations)} 处违规:")
    for v in violations:
        print(f"  - {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
