# ai-metrics —— AI 代码度量 + 提效同比 Demo

整合两个维度的度量，对应教程 [阶段 5 · 推广与度量](../../stage5.html)：

1. **AI 代码占比度量**（提炼自 `ai-code-ratio`）：用**三层识别算法**真实识别 AI 代码
2. **提效同比**（提炼自提效统计）：解析上线记录 Excel，算需求/Bug/人均的同比

## 快速运行

```bash
pip install -r requirements.txt   # openpyxl
python main.py
```

**预期**：自动生成示例 git 仓库 + Excel → 度量 AI 占比（含风格学反伪造）→ 提效同比 → 生成 `report.md`。

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

## 架构

```
ai-metrics/
├── detector/                 # 三层 AI 识别算法
│   ├── coauthored.py         # ① Co-authored-by 初筛
│   ├── stylometry.py         # ② 风格计量学（n-gram + 余弦相似度，反伪造）
│   └── registry.py           # ③ 检测器注册表
├── git_ratio.py              # git log 解析 → 检测 → AI 占比统计
├── efficiency.py             # Excel 解析 → 同比 → 人均
├── report.py                 # Markdown + HTML 报告
├── gen_data.py               # 生成示例 git + Excel 模板 + 示例数据
├── main.py                   # 一键编排
├── README.md, requirements.txt, .gitignore
└── workspace/                # 运行时产物（已 gitignore，不进版本库）
    ├── sample_repo/          # 示例 git 仓库（gen_data 初始化）
    ├── data/                 # Excel 模板 + 示例数据（gen_data 生成）
    └── report.md, report.html  # Markdown + HTML 报告（main 生成）
```

## 换成你自己的数据

1. **AI 占比**：改 `main.py` 里 `REPO` 指向你的 git 仓库（或 `git_ratio.measure("/path/to/your/repo")`）
2. **提效同比**：按 `workspace/data/template.xlsx` 录入你的上线记录，替换 `workspace/data/sample_releases.xlsx`

注：生产版 `ai-code-ratio` 用 Go 实现、TF-IDF 加权（IDF 来自全局语料）、Web 报告、多仓库；本 demo 用 Python 简化（TF + 单仓库 + Markdown），核心识别算法一致。
