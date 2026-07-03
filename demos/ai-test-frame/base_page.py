"""③ 测试基类 —— 通用操作库。

定位用 Playwright 推荐的通用策略（role / placeholder / label / text），
不绑死特定 UI 组件的 xpath——换被测系统时，只改这里的定位实现即可。
用例里 type=text/button/app/selector 会调到这些方法。
"""
from playwright.sync_api import Page
from assertions import AssertionCollector


class BasePage:
    def __init__(self, page: Page, assertions=None):
        self.page = page
        # 支持外部传入共享的 assertions，方便调度器统一收集所有 handler 的断言结果
        self.assertions = assertions or AssertionCollector(page=page)

    def click_app(self, data):
        """data={'key':'菜单/导航名'} —— 进入某个功能页"""
        self.page.get_by_text(data["key"]).first.click()

    def click_button(self, data):
        """data={'key':'按钮文本'}"""
        self.page.get_by_role("button", name=data["key"]).click()

    def input_text(self, data):
        """data={'key':'输入框占位符','val':'要输入的值'}"""
        self.page.get_by_placeholder(data["key"]).fill(str(data["val"]))

    def select_popup(self, data):
        """data={'key':'下拉框的 aria-label','val':'选项文本'}"""
        self.page.get_by_label(data["key"]).select_option(data["val"])
