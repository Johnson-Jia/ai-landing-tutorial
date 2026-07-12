# ai-metrics —— AI 提效四维度度量平台

整合**四维度**的度量，对应教程 [阶段 5 · 推广与度量](../../pages/stage5.html)：

| 维度 | 命令 | 解决什么 |
|---|---|---|
| ① code（AI 代码占比 + 提效同比）| `python main.py` / `--dim code` | 真实识别 AI 代码（三层算法 + 风格学反伪造）+ 需求/Bug/人均同比 |
| ② quality（输出质量）| `python main.py --dim quality` | code-grading + LLM-as-judge 评估 AI 输出 |
| ③ cost（API 成本）| `python main.py --dim cost` | FinOps：按 workspace 归因 + 缓存效率 + chargeback |
| ④ agent（Agent 效能）| `python main.py --dim agent` | 任务成功率/token 归因/工具反向评估 |
| 全部 | `python main.py --dim all` | 一次跑四维度 |

> 默认 `python main.py` = 维度 ①（AI 代码占比 + 提效同比，**向后兼容**，老用户无感）。
>
> 下文「核心一 / 核心二」分别讲维度 ① 的两块（AI 代码占比算法、提效同比模板），「核心三/四/五」对应维度 ②/③/④。

## 环境准备（先看完再跑）

跑这个 demo 需要两样东西：

1. **Python 3.8+**（下载：[python.org/downloads](https://www.python.org/downloads/)）。安装时 Windows 务必勾选 **Add Python to PATH**。用 `pip --version` 验证 pip 可用。
2. **git**（demo 里的 `main.py` 会自动生成一个示例 git 仓库来度量 AI 代码占比）。没装的去 [git-scm.com](https://git-scm.com/downloads) 下载。

**打开终端**：Windows 用 `cmd` / PowerShell；Mac 用 Terminal。

**进入目录**（关键）：先 `cd` 到本 demo 目录，否则找不到文件：

```bash
cd demos/ai-metrics
```

## 快速运行

确认 `cd` 进了 `demos/ai-metrics` 目录后，执行：

```bash
pip install -r requirements.txt   # openpyxl
python main.py
```

**预期**：自动生成示例 git 仓库 + Excel → 度量 AI 占比（含风格学反伪造）→ 提效同比 → 生成 `report.md`。

想跑另外三个维度（输出质量 / API 成本 / Agent 效能），加 `--dim` 参数（见开头表格），例如 `python main.py --dim all` 一次跑全四维度。

## 核心一：三层 AI 识别算法（为什么能真实识别 AI 代码）

只靠 Co-authored-by 不够（会被误标——VS Code Copilot 对手写代码也自动加 trailer）。本 demo 用三层算法：

| 层 | 文件 | 作用 |
|---|---|---|
| ① Co-authored-by 初筛 | `detector/coauthored.py` | commit message 含 AI 工具名 → 判 AI（置信度 1.0） |
| ② 风格计量学复核 | `detector/stylometry.py` | 算 AI 提交与作者本人风格画像的**余弦相似度**——像本人（sim 高）→ 可能误标，降置信度；不像本人（sim 低）→ 确认 AI |
| ③ 检测器注册表 | `detector/registry.py` | 组合①②，给出最终判定 |

**风格学是反伪造关键**：用"代码本身像不像作者本人手写"复核 Co-authored-by。算法（提炼自 ai-code-ratio 的 ngram.go / stylometry.go）：字符级 n-gram → TF 归一化 → 余弦相似度 → 置信度 = 1 − 相似度。

示例 git 仓库（`sample_repo/`，由 `gen_data.py` 生成）特意准备了三类提交演示：
- Alice 的**干净提交**（风格 A）→ 建风格画像
- Alice 的 **AI 提交**（风格 B + Co-authored-by）→ 与画像差异大 → 风格学维持较高置信度（确认 AI）
- Alice 的**误标提交**（风格 A + Co-authored-by）→ 与画像更像 → 风格学降低置信度（演示反伪造挡误标）

> 注：本 demo 用**极小代码样本**（每文件十余行）演示算法**机制**，两条 AI 提交的相似度差距较小；
> 生产环境（ai-code-ratio）在真实仓库、大量提交、长 diff 下，TF-IDF 风格学能有效拉开区分
> ——字符级 n-gram 需要足够样本量才稳定，这是算法特性，非缺陷。

## 核心二：提效同比 + Excel 模板

- `data/template.xlsx` 是**录入模板**：列 = 日期 / 定制或通用 / 应用 / 类型 / jira_id / 描述 / 开发人员。**按此模板录入你自己的上线记录**，放到 `data/`，即可被 `efficiency.py` 解析。
- `data/sample_releases.xlsx` 是示例（2025 基线 vs 2026 AI 推行后），开箱即跑。
- `efficiency.py` 算同比：上线条目 / 需求 vs Bug / 参与人数 / 人均条目。
  - 注：真实数据的开发人员字段常含多人、不规范写法（如「张三、李四」「张三（前端）」），生产环境需清洗去重才能得到准确的参与人数；demo 做简化处理（按逗号 split 去重），用真实数据时**人数会偏高**（实测约 2 倍），但上线/需求/Bug 数量与占比趋势准确。

## 核心三：输出质量评估（quality）

源自 cookbooks `building_evals`。AI 输出好不好不能只看占比，得**量化评估**。本 demo 提供两级评估：

- **code-grading（精确/正则）**：最快最可靠——把任务设计成可用代码自动评分（如「输出是否含正确函数名」「是否通过单测」）。
- **LLM-as-judge（开放性回答）**：对没有标准答案的开放性输出，用 LLM 当裁判，要求模型输出 `<correctness>pass|fail</correctness>` 标签便于自动解析。

核心哲学（提炼自 building_evals）：**尽量把任务设计成可代码自动评分**——精确匹配 > 正则 > LLM 判断，能用 code-grading 就别上 LLM-as-judge。

| 模块 | 作用 |
|---|---|
| `quality/grader.py` | 评分器：`code_grade`（精确/正则匹配）+ `llm_judge_prompt`（生成 judge 提示词）+ `judge`（解析 `<correctness>` 标签） |
| `quality/gen_testset.py` | 测试集模板（生成 / 录入评估用例） |
| `quality/run_eval.py` | 跑评估：批量调评分器 → 输出通过率统计 |

示例评估集 `quality/sample_evalset.json` 开箱即跑（`python main.py --dim quality`）。

## 核心四：API 成本可观测（cost · FinOps）

源自 cookbooks `observability/usage_cost_api`。AI 提效不能只看产出不看成​​本——按 workspace 归因费用、算缓存命中率、导出 chargeback CSV 给各部门"结账"，是 FinOps 的基本盘。

| 模块 | 作用 |
|---|---|
| `cost/admin_api.py` | Admin API 封装（拉取组织级用量）；**无 `ANTHROPIC_ADMIN_API_KEY` 时用 `sample_usage.json` 兜底**，演示完整流程 |
| `cost/chargeback.py` | 按 workspace 归因成本 + 导出 chargeback CSV |
| `cost/cache_efficiency.py` | 缓存命中率（prompt cache hit ratio）——单位 token 省下多少钱 |

无 Admin API key 也能跑：`cost/sample_usage.json` 提供样本数据，`python main.py --dim cost` 出完整 chargeback 报表。

## 核心五：Agent 效能（agent）

源自 cookbooks `tool_evaluation` 等。Agent 比「单次问答」复杂——一个任务跑多轮、调多个工具，光看 token 不够。本维度三层度量：

- **任务成功率 / 平均耗时**：Agent 干完没？多久干完？
- **token 按 agent 归因**：哪个 agent 烧 token（researcher vs coder）？
- **工具反向评估**：评估「**工具设计得好不好**」——同一个工具被多次调用，平均耗时多少、用户反馈（slow/ok）如何，反推工具 schema 是否合理。

| 模块 | 作用 |
|---|---|
| `agent/task_metrics.py` | 任务成功率、平均耗时 |
| `agent/token_usage.py` | 按 agent 归因 token 消耗 |
| `agent/tool_eval.py` | 工具反向评估（调用次数 / 平均耗时 / 反馈聚合） |

`python main.py --dim agent` 用内置样本跑通三层指标。

## 架构

```
ai-metrics/
├── detector/                 # ① 三层 AI 识别算法
│   ├── coauthored.py         # ① Co-authored-by 初筛
│   ├── stylometry.py         # ② 风格计量学（n-gram + 余弦相似度，反伪造）
│   └── registry.py           # ③ 检测器注册表
├── quality/                  # ③ 输出质量评估（building_evals）
│   ├── grader.py             # code_grade + llm_judge_prompt + judge
│   ├── gen_testset.py        # 测试集模板
│   ├── run_eval.py           # 跑评估 → 通过率
│   └── sample_evalset.json   # 示例评估集
├── cost/                     # ④ API 成本可观测（FinOps）
│   ├── admin_api.py          # Admin API 封装 + sample 兜底
│   ├── chargeback.py         # 按 workspace 归因 + CSV
│   ├── cache_efficiency.py   # 缓存命中率
│   └── sample_usage.json     # 示例用量数据
├── agent/                    # ⑤ Agent 效能（tool_evaluation）
│   ├── task_metrics.py       # 任务成功率 / 平均耗时
│   ├── token_usage.py        # 按 agent 归因 token
│   └── tool_eval.py          # 工具反向评估
├── git_ratio.py              # git log 解析 → 检测 → AI 占比统计
├── efficiency.py             # Excel 解析 → 同比 → 人均
├── report.py                 # Markdown + HTML 报告
├── gen_data.py               # 生成示例 git + Excel 模板 + 示例数据
├── main.py                   # 一键编排（--dim code|quality|cost|agent|all）
├── README.md, requirements.txt, .gitignore
└── workspace/                # 运行时产物（已 gitignore，不进版本库）
    ├── sample_repo/          # 示例 git 仓库（gen_data 初始化）
    ├── data/                 # Excel 模板 + 示例数据（gen_data 生成）
    ├── report.md, report.html  # ①② Markdown + HTML 报告（main 生成）
    └── chargeback.csv        # ④ chargeback CSV（--dim cost 生成）
```

## 换成你自己的数据

1. **AI 占比**：改 `main.py` 里 `REPO` 指向你的 git 仓库（或 `git_ratio.measure("/path/to/your/repo")`）
2. **提效同比**：按 `workspace/data/template.xlsx` 录入你的上线记录，替换 `workspace/data/sample_releases.xlsx`
3. **输出质量**：替换 `quality/sample_evalset.json` 为你的评估集（每条含 `expected` + `response` + 可选 `pattern`/`exact`）
4. **API 成本**：设环境变量 `ANTHROPIC_ADMIN_API_KEY` 走真实 Admin API；不设则用 `cost/sample_usage.json` 兜底
5. **Agent 效能**：替换 `main.py` 里 `run_agent_dim()` 内的 `tasks`/`usage`/`calls` 样本为你的 trace 数据

注：生产版 `ai-code-ratio` 用 Go 实现、TF-IDF 加权（IDF 来自全局语料）、Web 报告、多仓库；本 demo 用 Python 简化（TF + 单仓库 + Markdown），核心识别算法一致。**LLM-as-judge 真实接入（填 API key + 调真实模型）和真 Admin API 接入留作扩展点**——demo 用 sample 数据走通完整流程，接口已就绪。

## 常见报错（卡住了先看这里）

| 报错 | 原因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: No module named 'openpyxl'` | 依赖没装上 | 单独装一下：`pip install openpyxl`；仍失败多是国内源慢，换镜像：`pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `'git' 不是内部或外部命令` / git 找不到 | 没装 git，或没加进 PATH | 去 [git-scm.com](https://git-scm.com/downloads) 装上；装完重开终端，`git --version` 能出版本号就行 |
| 路径含中文/空格导致报错 | demo 生成临时仓库时对中文路径敏感 | 把整个 `ai-landing-tutorial` 放到**纯英文路径**下（如 `D:\projects\ai-landing-tutorial`），别放桌面/文档等含中文的目录 |
| `python: command not found` | Windows 上 Python 可能叫 `python3` 或 `py` | 换 `python3 main.py` 或 `py main.py` 试试 |
