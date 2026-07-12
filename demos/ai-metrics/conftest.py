"""让 tests 能 `from quality.xxx import ...` / `from cost.xxx import ...` 等。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
