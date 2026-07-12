"""让 tests/ 能 `from validate_brand import ...` 导入 scripts/ 下的模块。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
