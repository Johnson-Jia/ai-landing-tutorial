"""把文本中常见的非品牌色替换为最近的品牌色(规范化)。"""
from __future__ import annotations

import re
import sys

from validate_brand import BRAND_COLORS

HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _nearest(brand: list[tuple[int, int, int]], rgb: tuple[int, int, int]) -> str:
    """欧氏距离最近的品牌色。"""
    best = min(brand, key=lambda b: sum((a - c) ** 2 for a, c in zip(b, rgb)))
    return f"#{best[0]:02X}{best[1]:02X}{best[2]:02X}"


def apply(text: str) -> str:
    brand_rgb = [
        (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)) for h in BRAND_COLORS
    ]
    upper = {c.upper() for c in BRAND_COLORS}

    def repl(m: re.Match) -> str:
        hexv = m.group(0)
        if hexv.upper() in upper:
            return hexv
        rgb = (int(hexv[1:3], 16), int(hexv[3:5], 16), int(hexv[5:7], 16))
        return _nearest(brand_rgb, rgb)

    return HEX_RE.sub(repl, text)


def main(argv: list[str] | None = None) -> int:
    import argparse
    from pathlib import Path

    p = argparse.ArgumentParser(description="套用品牌色")
    p.add_argument("file")
    args = p.parse_args(argv)
    out = apply(Path(args.file).read_text(encoding="utf-8"))
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
