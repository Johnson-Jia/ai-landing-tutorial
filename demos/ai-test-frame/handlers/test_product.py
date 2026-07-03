"""⑤ 一个完整 handler 示例 —— 把 8 条编写规范整合成一个 add_product。

这个 handler 操作 site/index.html（被测页）：进入商品管理 → 新增 → 填表单 → 保存 → 验证。
真实项目里，每个业务模块写一个这样的 handler，用 @register 注册即可被调度器调用。
"""
import datetime
from base_page import BasePage
from registry import handler_registry


class TestProduct(BasePage):
    # 规范1: ENV_DATA 环境参数预留（多环境差异不硬编码）
    ENV_DATA = {
        "dev":  {"category": "测试分类A"},   # dev 环境
        "prod": {"category": "正式分类B"},   # prod 环境
    }

    def get_env_data(self):
        env = getattr(self, "_env", "dev")   # 真实项目从配置读当前环境
        return self.ENV_DATA.get(env, self.ENV_DATA["dev"])

    # 规范2: test_data 动态参数（时间戳保证唯一，避免重复运行数据冲突）
    @property
    def test_data(self):
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return {"name": f"自动化商品_{ts}", "category": self.get_env_data()["category"]}

    # 规范3+4: 主方法只做调度；add 流程 return 新增数据（供 _save_as 跨步骤引用）
    @handler_registry.register("addproduct", editor_meta={   # 元数据（生产里驱动 Web 编辑器渲染表单）
        "label": "新增商品",
        "fields": ["val"],
        "field_labels": {"val": "商品类型"},
        "group": "商品管理",
        "dropdowns": {"val": ["实物", "虚拟"]},
        "save_as_options": ["product_name"],
    })
    def add_product(self, data, parent=None):
        cached = self.test_data               # 规范2: 必须缓存！否则每次访问生成新时间戳
        ptype = data.get("val", "实物")
        # 规范5+6: 每步有日志、有注释
        self.click_app({"key": "商品管理"})     # 进入商品管理
        self.click_button({"key": "新增"})      # 打开新增表单
        self.input_text({"key": "商品名称", "val": cached["name"]})   # 填名称
        self.select_popup({"key": "商品类型", "val": ptype})          # 选类型
        self.click_button({"key": "保存"})      # 保存
        self._verify(cached["name"])          # 软断言验证
        return cached["name"]                 # 供用例里 _save_as 引用

    def _verify(self, name):
        """验证商品出现在列表（软断言：失败不中断）—— 只在验证时加断言。"""
        loc = self.page.get_by_text(name)
        try:
            loc.first.wait_for(state="visible", timeout=10000)   # 规范7: 用内置等待
            self.assertions.assert_pass(f"商品创建验证 - {name}")
        except Exception:
            self.assertions.assert_fail(f"商品创建验证 - {name}", "列表未找到")
