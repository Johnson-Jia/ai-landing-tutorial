"""② 软断言 —— 失败不抛异常、不中断后续步骤，自动截图 + 收集结果，最后统一汇总。

对比硬断言（assert，失败即停）：软断言让一条用例里的多个验证都能跑完，
失败的全记进报告，更贴近「记录问题」而非「一错就停」的测试诉求。

注：输出用纯文本标记（[通过]/[失败]）而非 emoji，兼容 Windows GBK 控制台。
"""
import time


class AssertionCollector:
    def __init__(self, page=None, screenshot_dir="."):
        self._results = []
        self.page = page
        self.screenshot_dir = screenshot_dir

    def assert_pass(self, name):
        self._results.append({"name": name, "status": "PASS"})
        print(f"  [通过] {name}")

    def assert_fail(self, name, err=""):
        shot = None
        if self.page:  # 失败自动截图
            try:
                shot = f"{self.screenshot_dir}/fail_{int(time.time()*1000)%100000}.png"
                self.page.screenshot(path=shot)
            except Exception:
                shot = None
        self._results.append({"name": f"{name} - {err}", "status": "FAIL", "shot": shot})
        print(f"  [失败] {name} {err}")

    def assert_info(self, name, info=""):
        self._results.append({"name": f"{name} - {info}", "status": "INFO"})
        print(f"  [信息] {name} {info}")

    def drain(self):
        """取走结果并清空（避免用例间数据污染）。"""
        r, self._results = self._results, []
        return r
