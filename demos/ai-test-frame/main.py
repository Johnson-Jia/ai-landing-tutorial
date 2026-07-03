"""⑦ 执行入口 —— 打开被测页 → 跑用例 → 汇总断言。

导入 handlers 即触发 @register 注册（生产版可做成自动扫描 test_*.py，这里显式导入更直观）。
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from runner import TestRunner
import handlers.test_product   # 导入即注册 addproduct（更多 handler 往这里加）

HERE = Path(__file__).parent
WORK = HERE / "workspace"               # 运行时产物（失败截图等）单独放这里，不污染源码
SITE = (HERE / "site" / "index.html").resolve()
CASES = HERE / "data" / "cases.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_context().new_page()
    page.goto(SITE.as_uri())           # file:// 打开本地被测页（demo 自带，开箱即跑）
    WORK.mkdir(exist_ok=True)
    runner = TestRunner(page, str(CASES), screenshot_dir=str(WORK))
    runner.run()
    # 汇总断言（生产版会生成 HTML 报告）
    results = runner.base.assertions.drain()
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"\n{'='*50}")
    print(f"汇总: 通过 {passed}, 失败 {failed}")
    print(f"{'='*50}")
    browser.close()
