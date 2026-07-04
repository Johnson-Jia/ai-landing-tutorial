# ai-test-frame —— 最小可运行的 AI 自动化测试框架

教程《[AI 自动化测试：方法论与实践](../../assets/ref/AI自动化测试-方法论与实践.html)》§8「动手实践」的可运行落地。
体现「**AI 在编码期生成测试资产、运行期确定性执行**」的完整架构，**开箱即跑**。

## 环境准备（先看完再跑）

跑这个 demo 需要三样东西，缺一个都起不来：

1. **Python 3.8+**（下载：[python.org/downloads](https://www.python.org/downloads/)）。安装时 Windows 务必勾选 **Add Python to PATH**，否则命令行找不到 python。
2. **git**（用于 demo 内部生成示例仓库）。没装的去 [git-scm.com](https://git-scm.com/downloads) 下载。
3. **pip**（Python 的包管理器，装 Python 时自带）。验证一下：

   ```bash
   pip --version
   ```

   能打印出 pip 版本号就 OK。

**打开终端的方式**：
- Windows：按 `Win+R` 输入 `cmd` 或用 PowerShell
- Mac：应用程序 → 实用工具 → 终端（Terminal）

**进入目录**（关键，很多人卡在这）：终端里先 `cd` 到本 demo 目录再运行命令，否则会找不到文件：

```bash
# 把下面路径换成你电脑上的实际路径
cd demos/ai-test-frame
```

## 快速运行

确认 `cd` 进了 `demos/ai-test-frame` 目录后，依次执行：

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

## 常见报错（卡住了先看这里）

| 报错 | 原因 | 解决 |
|---|---|---|
| `'pip' 不是内部或外部命令` / `pip: command not found` | 装 Python 时没勾 Add to PATH | 重装 Python，安装界面**勾选 Add Python to PATH**，或手动把 Python 安装目录加进系统环境变量 |
| `playwright install chromium` 下载超时 / 卡住不动 | 国内访问 Chromium 下载源慢 | 重试几次；或设镜像：`set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`（Mac/Linux 用 `export`）后重跑 |
| `ModuleNotFoundError: No module named 'xxx'` | 没 `cd` 进 demo 目录，或没装依赖 | 确认终端当前在 `demos/ai-test-frame`（`pwd` 看一下），再重跑 `pip install -r requirements.txt` |
| `python: command not found` | Windows 上 Python 可能叫 `python3` 或 `py` | 换 `python3 main.py` 或 `py main.py` 试试 |
