# Agent Teams 操作手册

> 版本 2.1 · 适用:Claude Code CLI / Desktop / IDE · 作者:Johnson

一条命令拉起一个多 Agent 团队,把复杂任务自动拆成 6 步跑完。本手册给你(读者)通读用;AI 运行时读的是同目录的 `SKILL.md`,细节按需读 `reference/`。

---

## 一、快速开始

### 触发方式

| 方式 | 示例 |
|---|---|
| 斜杠命令 | `/agent-teams 开发用户认证功能` |
| 直接对话 | "帮我拉个团队做 XX"、"多 agent 并行开发 XX" |

**触发关键词**:多 agent、agent 协作、agent 编排、并行 agent、分工协作、拉团队、拉个团队、跨项目、多项目协作。

### 是否应该用

| 适合用 | 不适合用 |
|---|---|
| 跨文件重构、多维度审查 | 单文件小修改 |
| 大规模代码生成、并行处理 | 简单问答 |
| 需要多角色协作的复杂任务 | 单 agent 就能完成的任务 |

---

## 二、6 步执行流程

```
[1/6] 环境检测 ──→ [2/6] 任务分析+蓝图 ──→ [3/6] 用户确认(必须)
                                                       │
[6/6] 结果交付 ←── [5/6] 质量验收 ←── [4/6] 并行执行
```

| 步骤 | 做什么 | 你需要做什么 |
|---|---|---|
| [1/6] 环境检测 | 检查项目初始化、注册表、跨项目、Swarm | 首次确认初始化 |
| [2/6] 任务分析 | 分析需求、选策略、输出团队蓝图 | 审阅蓝图 |
| [3/6] 用户确认 | 展示计划等待确认 | **确认或修改** |
| [4/6] 并行执行 | 调度 Agent 并行工作 | 等待(失败会通知你) |
| [5/6] 质量验收 | 对照验收标准逐项检查 | 无 |
| [6/6] 结果交付 | 输出执行报告 | 审阅结果 |

### 需要你确认的时刻

执行中有 **5 个确认点**,会以醒目方式提示:

```
> ### ⚠️ 需要确认:项目初始化    ← [1/6] 首次运行
> ### ⚠️ 需要确认:Stage N 完成   ← devflow 驱动模式
> ### 🔴 必须确认:即将执行        ← [3/6] 执行前(不可跳过)
> ### ⚠️ Agent 执行失败           ← [4/6] Agent 出错时
> ### ⚠️ 需要确认:devflow 交接    ← [6/6] devflow 模式完成时
```

只有 🔴 那个**不可跳过**——没拿到你的确认,不会启动执行。其余 ⚠️ 是重要决策点,等你回复。

### 验收阶段([5/6])

验收标准来自 [2/6] 蓝图里的「验收标准」列,逐项检查:

```
[5/6] 质量验收
  ✅ 标准1: 通过
  ✅ 标准2: 通过
  ❌ 标准3: 不通过 → 打回修改(最多2轮)
```

不通过 → 打回对应 Agent(最多 2 轮)→ 仍不通过 → 通知你介入。

### 交付阶段([6/6])

```
[6/6] 执行报告
  成功: Y/Z | 失败: X/Z
  ✅ 角色1: 结果
  ✅ 角色2: 结果
  汇总: 综合结论
  建议: 后续方向
  [Swarm 清理: TeamDelete()]  ← Swarm 模式时
```

### Agent 状态追踪

[4/6] 会实时显示每个 Agent 的状态:

| 标记 | 含义 |
|---|---|
| 🚀 | 启动中(显示 subagent_type 和模型) |
| ⏳ | 运行中 |
| ✅ | 完成(显示修改文件数) |
| ❌ | 失败(显示原因) |

多 Agent 并行时展示实时进度面板:

```
执行进度:
  #1 architect  ✅ 完成 (接口文档,2个文件)
  #2 backend    ⏳ 运行中...
  #3 frontend   🚀 等待 #1 结果...
```

### Swarm 协作模式

当 Swarm 可用时(环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`),复杂任务自动用 Swarm 模式:

| 维度 | 标准并行 | Swarm 协作 |
|---|---|---|
| 通信 | 单向(通知回主会话) | 双向(Leader ↔ Member) |
| 异常 | 通知你决定 | Leader 自主决策 |
| 任务分配 | prompt 内固定 | Leader 动态调整 |
| 适用 | 一轮完成的独立任务 | 多轮协调、动态调整 |

工作流:`TeamCreate` → Leader(SendMessage 分配/处理异常)→ Member × N(执行/汇报)→ Leader 查 TaskList → 下一轮 → 全完成 → `TeamDelete` 清理。

> Swarm 是 Lead-Member 的增强版:env var 已设时,Lead-Member 自动升级为 Swarm。

---

## 三、编排策略

自动选择,也可直接指定。

| 策略 | 适用 | 怎么做 |
|---|---|---|
| 直接调用 | 有 Skill 完全覆盖需求 | 直接 `Skill()`,不组队 |
| **标准并行(默认)** | 中等/复杂任务 | 分析→确认→并行→验收 |
| Lead-Member | 需要进度跟踪或多轮协调 | Leader 用 TaskCreate/Update 全程跟踪 |
| **Swarm 协作** | Swarm 可用 + 多轮协调 | TeamCreate + SendMessage 双向通信 |

**指定策略**:对话里说"用标准并行"或"策略2"可跳过自动选择。

---

## 四、团队模板与模型速查

### 团队模板(4 个)

| 模板 | 角色数 | 适用场景 |
|---|---|---|
| full-stack-team | 4 | 前后端协作新功能 |
| code-review-team | 3-4 | 大规模代码审查 |
| refactor-team | 3-5 | 跨文件重构 |
| cross-project-fullstack | 4 | 前后端分属不同仓库 |

### 模型与 subagent_type

| 模型 | 用途 |
|---|---|
| `opus` | 架构、安全、复杂推理 |
| `sonnet` | 常规开发(默认) |
| `haiku` | 简单验证、初筛、打分 |

| subagent_type | 用途 |
|---|---|
| `general-purpose` | 默认,复杂多步骤 |
| `Explore` | 只读搜索分析 |
| `Plan` | 只读架构设计 |
| `code-reviewer` | 代码审查 |

> 团队自定义类型(如前端专项)需团队预置到 `.claude/agents/`;不存在时回退 `general-purpose`。各模板的角色构成详见 `reference/team-and-registry.md`。

---

## 五、项目注册表

**一次配置,多次复用** —— `.claude/project-registry.json`,agent-teams 自动感知关联项目。

### 配置示例

```json
{
  "version": 1,
  "projects": [
    { "name": "app-backend", "path": ".",             "role": "当前项目", "type": "java"  },
    { "name": "app-sibling", "path": "../app-sibling", "role": "关联服务", "type": "java"  },
    { "name": "app-mobile",  "path": "../app-mobile",  "role": "移动端",   "type": "node" }
  ]
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 项目标识 |
| `path` | 是 | 项目路径(`"."`=当前项目) |
| `role` | 否 | 项目角色,辅助任务分配 |
| `description` | 否 | 注入 Agent 上下文 |
| `type` | 否 | java/node/python/mixed,影响 subagent_type |

### 工作原理

```
[1/6] 环境检测时自动执行:
  1. 读取注册表 → 路径验证(ls -d)
  2. 增量同步:扫描 ../*/ 发现未注册 git 仓库 → 自动追加
  3. 结合任务分析涉及哪些项目 → 模糊时询问用户
  4. Agent prompt 自动填充项目信息(路径、CLAUDE.md、技术栈)
```

### 首次自动初始化

首次运行自动检测并补全缺失文件:

| 缺失文件 | 自动动作 |
|---|---|
| `.claude/CLAUDE.md` | 扫描项目结构 → 生成标准 CLAUDE.md → 展示确认 |
| `.claude/project-registry.json` | 全量扫描兄弟 git 项目 → 自动注册 → 展示确认 |

```
> ### ⚠️ 需要确认:项目初始化
> CLAUDE.md / 注册表 已自动生成,请审阅上方内容。
> 👉 请回复:`确认` 保存 | `修改` 补充信息 | `跳过` 不生成
```

**增量同步**:后续每次运行,自动检测兄弟目录是否有新项目 → 自动追加。可随时编辑注册表补充 `role` 和 `description`。

---

## 六、操作示例

### 示例 1:标准并行(完整流程)

见 [`examples/blueprint-example.md`](../examples/blueprint-example.md)——用户认证功能(注册 + 登录 + JWT),展示了从 [1/6] 到 [6/6] 的完整对话,含 Agent 失败重试。

### 示例 2:跨项目协作(注册表驱动)

```
用户: /agent-teams 给订单系统加售后通知功能,要改后端和移动端

Claude: [1/6] 环境检测
        初始化: ✅
        模式: 独立
        范围: 跨项目(app-backend, app-mobile)
        注册表: 已加载(3 个关联项目)
        Swarm: ❌ 未启用

        分析任务涉及项目:
        - "后端"   → app-backend
        - "移动端" → app-mobile

      [2/6] 团队蓝图(注册表自动填充项目信息):
        | # | 角色        | 项目        | 职责           | 依赖 |
        | 1 | api-designer | app-backend | 设计通知接口   | 无   |
        | 2 | be-dev      | app-backend | 实现通知逻辑   | #1   |
        | 3 | mobile-dev  | app-mobile  | 通知页面       | #1   |

      > ### 🔴 必须确认:即将执行
      > 👉 请回复:`确认` 开始执行 | `修改` 调整蓝图

用户: 确认

Claude: [4/6] 执行 — #1 先行 → #2,#3 并行
        ... (省略进度面板) ...
      [5/6] 质量验收...全部通过
      [6/6] 执行报告: 成功 3/3
```

### 示例 3:Swarm 协作

```
用户: /agent-teams 多 agent 团队开发后台管理模块,含 CRUD、报表、数据导出,前后端要联调

Claude: [1/6] 环境检测
        Swarm: ✅ 可用

      [2/6] 任务分析(检测到多轮协调需求 + Swarm 可用 → Swarm 模式)
        团队蓝图(Swarm):
        | # | 角色        | 职责          | 模型   |
        | L | leader      | 协调分配      | opus   |
        | 1 | api-dev     | 模块 CRUD     | sonnet |
        | 2 | report-dev  | 报表          | sonnet |
        | 3 | export-dev  | 导出          | sonnet |
        | 4 | frontend    | 页面 + 联调   | sonnet |

      > ### 🔴 必须确认:即将执行(Swarm 模式)
      > Leader 将自主协调任务分配和异常处理。
      > 👉 请回复:`确认` 开始执行 | `修改` 调整蓝图

用户: 确认

Claude: [4/6] Swarm 执行
        🏗️ TeamCreate("plan-module")
        🚀 leader / api-dev / report-dev / export-dev / frontend 启动...
        (Leader 发现 frontend 需要联调 → 动态追加联调任务 → 通知 frontend)
        🧹 TeamDelete() 清理
      [6/6] 执行报告: 成功 4/4
```

> Swarm 的优势:Leader 发现联调需求后动态追加任务,**无需中断等你决策**。

### 示例 4:Agent 执行失败

```
Claude: [4/6] 并行执行
        执行进度:
          #1 architect ✅ 完成 (接口文档,2个文件)
          #2 backend   ❌ 失败: 缺少通知表 DDL,DAO 层无法生成

        > ### ⚠️ Agent 执行失败
        > backend 执行失败:缺少通知表 DDL,DAO 层无法生成
        > 👉 请选择:`重试` | `跳过` 该任务 | `终止` 全部

用户: 重试,补充表结构:t_notification(notice_id, biz_id, user_id, notice_type, ...)

Claude: 🚀 backend 重试中...
        #2 backend ✅ 完成 (通知 DAO,3个文件)
```

---

## 七、devflow 集成速查(可选)

> devflow 是教程 `claude-skills` 内的 6 阶段开发流程 skill。装了它,agent-teams 接管 Stage 4(执行),其余交接回 devflow。

### 4 种运行模式

| 模式 | 检测条件 | 行为 |
|---|---|---|
| 独立 | devflow 未安装 | 正常 6 步流程 |
| **devflow 驱动** | devflow 已装 + 无工件 | 逐 Stage 调 brainstorming→openspec-propose→writing-plans |
| 完整集成 | devflow 已装 + Plan + specs | 直接从 Plan 按 Capability 生成蓝图 |
| 半集成 | devflow 已装 + 只有 specs | 先补 Plan → 再生成蓝图 |

### 分工边界

| 阶段 | 负责方 |
|---|---|
| Stage 1-3(规划) | agent-teams 调 devflow 底层 skill |
| Stage 4(执行) | agent-teams 并行 Agent |
| Stage 5-6(验证 + 归档) | 交接回 devflow |

### 安全边界
- 只读 devflow / OpenSpec 工件
- 只写 Plan 的 `### [x]` 标记
- **禁止** git commit(由 devflow 统一管理)

---

## 八、故障处理速查

| 问题 | 怎么办 |
|---|---|
| Agent 执行失败 | 通知你,提供重试 / 跳过 / 终止 |
| Skill 找不到 | 回退链:本地 → find-skills → 通用 Agent |
| 质量不达标 | 打回修改最多 2 轮,仍不过人工介入 |
| 跨项目文件误操作 | prompt 限定路径 + 事后 git diff 检查 |
| 注册表路径不可达 | 跳过该项目并警告,不影响其他 |
| Swarm 不可用 | 自动回退标准 Agent 调度 |
| Swarm Member 无响应 | Leader 等待 → SendMessage 确认 → 升级主会话 |

---

*手册 v2.1 · 配套:`SKILL.md`(AI 入口)· `reference/`(细节)· `examples/`(样例)*
