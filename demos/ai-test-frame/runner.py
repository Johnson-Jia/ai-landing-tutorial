"""④ 数据驱动调度器 —— 读用例数据 → running 开关 → 按 type 路由
（基础操作走字典、模块操作走注册中心）→ ${变量} 解析 → 延迟加载实例 → 收集结果。

这一层把「用例数据」和「执行代码」彻底解耦：运营在 data/cases.json 编步骤，
调度器按 type 自动找到对应方法执行。
"""
import json
import re
from base_page import BasePage
from registry import handler_registry


class TestRunner:
    def __init__(self, page, data_path: str, screenshot_dir: str = "."):
        self.page = page
        self.base = BasePage(page)            # 基础操作实例
        self.base.assertions.screenshot_dir = screenshot_dir   # 失败截图目录（main 传 workspace/）
        self.ctx = {}                         # 跨行变量上下文（_save_as 保存的值）
        self._instances = {}                  # 模块操作实例池（延迟加载、复用）
        with open(data_path, encoding="utf-8") as f:
            self.cases = json.load(f)

    # 基础操作 type -> 基类方法名（模块操作则走注册中心）
    BASIC = {
        "text": "input_text",
        "button": "click_button",
        "app": "click_app",
        "selector": "select_popup",
    }

    def run(self):
        for i, row in enumerate(self.cases):
            data_json = str(row.get("data_json", "")).strip()
            running = str(row.get("running", "是")).strip()
            if not data_json or running == "否":
                continue                      # 空行 / 关闭的用例跳过
            print(f"\n=== 用例 第{i+1}条 ===")
            self._exec_row(json.loads(data_json))

    def _exec_row(self, steps: list):
        for step in steps:
            step = self._resolve_vars(step)   # ${变量} 替换
            t = step["type"]
            try:
                if t in self.BASIC:
                    # 1) 基础操作走字典
                    handler = getattr(self.base, self.BASIC[t])
                else:
                    # 2) 模块操作走注册中心
                    info = handler_registry.get(t)        # (方法名, 函数)
                    if not info:
                        self.base.assertions.assert_fail(f"未知 type {t}", "未注册")
                        continue
                    name, func = info
                    # 延迟加载：handler 是实例方法，必须先有实例再取绑定方法
                    # 类引用在这里延迟解析（装饰器执行时类还没定义完，那时解析会拿到 None）
                    if t not in self._instances:
                        class_name = func.__qualname__.split('.')[0]
                        class_ref = func.__globals__.get(class_name)
                        # 传入共享的 assertions，让所有 handler 的断言结果汇总到一处
                        self._instances[t] = class_ref(self.page, assertions=self.base.assertions)
                    handler = getattr(self._instances[t], name)
                result = handler(step)
                if "_save_as" in step and result is not None:
                    self.ctx[step["_save_as"]] = result   # 保存供后续步骤/用例引用
            except Exception as e:
                self.base.assertions.assert_fail(t, str(e))

    def _resolve_vars(self, step: dict) -> dict:
        """把 ${name} 替换成 self.ctx 里的值（步骤间/用例间变量传递）。"""
        s = dict(step)
        for k, v in s.items():
            if isinstance(v, str) and "${" in v:
                s[k] = re.sub(
                    r"\$\{(\w+)\}",
                    lambda m: str(self.ctx.get(m.group(1), m.group(0))),
                    v,
                )
        return s
