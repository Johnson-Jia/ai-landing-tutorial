"""① 注册中心 —— 装饰器把方法注册成用例里的一个 type，调度器按 type 取 handler。

核心模式（提炼自企业级测试框架）：
  - @register 装饰器把方法登记进全局表（存方法名 + 函数引用）
  - 调度器按 type 取出函数，再延迟解析其所属类、创建实例（handler 是实例方法）
  - 注意：不在装饰器里解析「类引用」——类定义执行到方法装饰器时，类名尚未绑定到
    模块 globals，会拿到 None。类引用改在调度器创建实例时延迟解析（那时类已定义完）。
"""
from typing import Dict, Optional, Tuple, Callable


class HandlerRegistry:
    def __init__(self):
        self._methods: Dict[str, Tuple[str, Callable]] = {}  # type -> (方法名, 函数)
        self._metas: Dict[str, dict] = {}                    # type -> editor_meta

    def register(self, type_name: str, editor_meta: dict = None):
        """装饰器：把方法注册成用例里的一个 type。"""
        def deco(func):
            self._methods[type_name] = (func.__name__, func)
            if editor_meta:
                self._metas[type_name] = editor_meta
            return func
        return deco

    def get(self, type_name: str):
        """返回 (方法名, 函数)，未注册返回 None。"""
        return self._methods.get(type_name)

    def get_meta(self, type_name: str) -> Optional[dict]:
        return self._metas.get(type_name)


# 全局单例：所有 handler 模块导入时即向它注册
handler_registry = HandlerRegistry()
