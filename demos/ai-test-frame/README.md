# ai-test-frame —— 最小可运行的 AI 自动化测试框架

教程《[AI 自动化测试：方法论与实践](../../assets/ref/AI自动化测试-方法论与实践.html)》§8「动手实践」的可运行落地。
体现「**AI 在编码期生成测试资产、运行期确定性执行**」的完整架构，**开箱即跑**。

## 快速运行

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```

**预期**：Playwright 打开 `site/index.html`（自带的极简商品管理页），按 `data/cases.json` 跑用例（新增商品 → 验证列表出现），终端输出断言汇总：

```
=== 用例 第1条 ===
=== 用例 第2条 ===
  ✅ 商品创建验证 - 自动化商品_xxxxxx
=== 用例 第3条 ===
  ✅ 商品创建验证 - 自动化商品_xxxxxx
==================================================
📊 汇总: 通过 2, 失败 0
==================================================
```

## 架构（每个文件对应一个核心模块）

| 文件 | 作用 | 体现的核心架构 |
|---|---|---|
| `registry.py` | 注册中心 | 装饰器注册 + 类引用 + get（type→handler 映射） |
| `assertions.py` | 软断言 | 失败不中断 + 截图 + 收集结果 |
| `base_page.py` | 测试基类 | 通用操作 + 通用定位（role / placeholder / label） |
| `runner.py` | 数据驱动调度器 | 读用例 + type 路由 + `${变量}` + 延迟加载实例 |
| `handlers/test_product.py` | handler 示例 | 8 条规范整合 + editor_meta |
| `main.py` | 执行入口 | 开浏览器 → 跑用例 → 汇总 |
| `data/cases.json` | 用例数据 | 步骤 JSON + running 开关 |
| `site/index.html` | 被测页 | 极简商品管理（自带，开箱跑） |

> 📁 **运行产物分离**：失败截图等运行时产物放 `workspace/`（已 gitignore，不进版本库）；`site/`（被测页）和 `data/`（用例）是 demo 自带资产，保留原位。

## 体现的关键思想

1. **AI 只生成不执行**：handler（如 `test_product.py`）由「录制 → AI 转换 → 人审」在编码期产出；运行期是确定性的数据驱动调度（`runner.py`），零 AI——规避幻觉导致的"虚假通过"。
2. **数据与代码解耦**：用例在 `data/`，handler 在 `handlers/`，调度器按 `type` 路由——运营编步骤，不碰代码。
3. **注册中心模式**：handler 用 `@register` 登记，调度器自动发现，新增模块零改调度器。
4. **软断言**：失败不中断，一条用例的多个验证都跑完、全记进报告。
5. **变量传递**：`_save_as` + `${name}` 让步骤间/用例间传递数据。

## 换成你自己的被测系统

demo 自带 `site/index.html` 是为了开箱即跑。真实使用时：

1. 改 `base_page.py` 的定位，匹配你系统的 UI（保持通用定位策略）
2. 改 `main.py` 的 `page.goto()` 指向你的系统，并加登录
3. 照 `test_product.py` 的写法，为你的业务写更多 handler
4. 在 `data/` 编用例（生产可用 Excel + pandas 替代 JSON，数据驱动思想一致）
