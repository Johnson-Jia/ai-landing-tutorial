"""让 tests/ 下的测试能用 `from chunking import ...` 导入同目录模块。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
