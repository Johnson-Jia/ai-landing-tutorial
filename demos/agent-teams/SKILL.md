---
name: agent-teams
description: "多 Agent 并行编排 skill。一条命令拉起团队做完复杂任务:环境检测→分析蓝图→确认→并行执行→质量验收→交付。编排 Claude Code 原生 Agent 工具,自己不实现业务逻辑。触发:/agent-teams,或 多agent/拉团队/并行/跨项目/分工协作 等关键词。"
license: MIT
compatibility: 需 Claude Code Agent 工具;Swarm 可选(需 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1);devflow 集成需预装 devflow skill
metadata:
  author: Johnson
  version: "2.2"
---

<!-- 设计原则:①编排不实现(只调度,不写业务逻辑) ②确认闸门(🔴 点不可跳过) ③优雅降级(每个可选依赖都有回退) -->

# Agent Teams

多 Agent 并行编排 skill。把「跨文件重构 / 大规模审查 / 多角色协作」等复杂任务,拆成 6 步流程自动跑完。**自己不实现业务逻辑**,只调度 Claude Code 原生 Agent 工具(+ 可选 Swarm / devflow)。

> 这是**编排型 skill**——价值在 4 个设计手法:①编排不实现 ②人在回路确认闸门 ③项目注册表跨项目复用 ④优雅降级。

## 是否应该用

| 适合用 | 不适合用 |
|---|---|
| 跨文件重构、多维度审查 | 单文件小修改 |
| 大规模代码生成、并行处理 | 简单问答 |
| 多角色协作的复杂任务 | 单 agent 可完成的任务 |

## 6 步执行流程

```
[1/6] 环境检测 ──→ [2/6] 任务分析+蓝图 ──→ [3/6] 用户确认(必须)
                                                       │
[6/6] 结果交付 ←── [5/6] 质量验收 ←── [4/6] 并行执行
```

### [1/6] 环境检测

触发后第一件事,检查并输出环境状态块:

1. **项目初始化**:读 `.claude/CLAUDE.md`,缺失则扫描项目结构生成 → 进首次初始化确认。
2. **项目注册表**:读 `.claude/project-registry.json`,缺失则扫描兄弟 git 项目(`ls -d ../*/`)自动注册 → 进首次初始化确认。路径不可达 → 跳过该项目并警告。详见 `reference/team-and-registry.md`。
3. **Swarm 检测**:检查环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`。已设 → Swarm 可用;未设 → 标记不可用,后续回退标准并行。
4. **devflow 检测**(可选):检查项目是否装了 devflow skill(有 `openspec/` 或 devflow 工件)。有 → devflow 集成模式;无 → 独立模式。

输出:
```
[1/6] 环境检测
  初始化: ✅
  模式: 独立 | devflow驱动 | 完整集成 | 半集成
  范围: 单项目 | 跨项目(app-backend, app-sibling, ...)
  注册表: 已加载(N 个) | 首次初始化
  Swarm: ✅ 可用 | ❌ 未启用(将回退标准并行)
```

> `模式` 字段 4 值(独立 / devflow 驱动 / 完整集成 / 半集成)的判定规则见 `reference/orchestration.md` §3。

**⚠️ 需要确认:项目初始化**(仅首次):
```
> ### ⚠️ 需要确认:项目初始化
> CLAUDE.md / 注册表 已自动生成,请审阅上方内容。
> 👉 请回复:`确认` 保存 | `修改` 补充信息 | `跳过` 不生成
```

### [2/6] 任务分析 + 团队蓝图

1. 解析需求,判断涉及哪些项目(结合注册表;模糊则询问用户)。
2. 选编排策略(决策树见下「编排策略」)。
3. 按团队模板生成蓝图:角色 / 职责 / 模型 / subagent_type / 依赖。模板见 `reference/team-and-registry.md`。
4. **为每个角色定义「验收标准」列**——[5/6] 据此验收。

输出示例:
```
团队蓝图:
| # | 角色    | 职责     | 模型    | subagent_type   | 依赖 | 验收标准                 |
| 1 | architect | 接口设计 | opus    | Plan            | 无   | 产出接口文档,覆盖全部用例 |
| 2 | backend  | 接口实现 | sonnet  | general-purpose | #1   | 实现接口,单测通过        |
| 3 | frontend | 页面开发 | sonnet  | general-purpose | #1   | 页面联通接口,可演示      |
| 4 | tester   | 用例验证 | haiku   | general-purpose | #2,#3| 单测覆盖核心用例        |
```

### [3/6] 用户确认(🔴 必须,不可跳过)

```
> ### 🔴 必须确认:即将执行
> 以上为完整团队计划,确认后将立即启动 Agent 执行。
> 👉 请回复:`确认` 开始执行 | `修改` 调整蓝图
```

**未获确认不得进入 [4/6]**。用户 `修改` → 回 [2/6] 调整。

### [4/6] 并行执行

按依赖拓扑派 Agent:无依赖并行启动,有依赖等前置完成再启动。Swarm 可用则用 TeamCreate(见 `reference/orchestration.md`)。

实时进度面板:
```
🚀 architect 启动中...(Plan / opus)
🚀 backend   启动中...(general-purpose / sonnet)

执行进度:
  #1 architect  ✅ 完成 (接口文档,2个文件)
  #2 backend    ⏳ 运行中...
  #3 frontend   🚀 等待 #1 结果...
```

**⚠️ Agent 执行失败**(默认阻塞等待用户回复,不自动超时):
```
> ### ⚠️ Agent 执行失败
> backend 执行失败:<原因>
> 👉 请选择:`重试` | `跳过` 该任务 | `终止` 全部
```

### [5/6] 质量验收

对照 [2/6] 蓝图「验收标准」列逐项检查:
```
[5/6] 质量验收
  ✅ 标准1: 通过
  ✅ 标准2: 通过
  ❌ 标准3: 不通过 → 打回修改(最多2轮)
```

- devflow 模式额外:遍历 `specs/<capability>/spec.md` 逐条验证。
- ❌ → **打回对应 Agent(重新派同一 Agent,携带失败原因)→ 重新验收**。**最多 2 轮**,仍 ❌ → 通知用户介入。

### [6/6] 结果交付

```
[6/6] 执行报告
  成功: Y/Z | 失败: X/Z
  ✅ 角色1: <结果>
  ✅ 角色2: <结果>
  汇总: <综合结论>
  建议: <后续方向>
  [Swarm 清理: TeamDelete()]  ← Swarm 模式时
```

devflow 模式额外:
```
> ### ⚠️ 需要确认:devflow 交接
> Plan 已同步 [x] 标记,agent-teams 执行完毕。
> 👉 请选择:`交接` 回 devflow Stage 5-6 | `结束`
```

## 确认点统一格式

5 个确认点用一致醒目块,保证人在回路:

| 标记 | 含义 | 出现时机 |
|---|---|---|
| 🔴 必须确认 | 不可跳过,未确认不执行 | [3/6] 执行前 |
| ⚠️ 需要确认 | 重要决策,等用户回复 | [1/6]首次 / devflow Stage / [4/6]失败 / [6/6]交接 |

```
> ### 🔴/⚠️ <标题>
> <内容>
> 👉 请回复:`选项A` | `选项B` | ...
```

## 编排策略(自动选择)

```
任务有 Skill 完全覆盖?
  → 是 → 直接调用(不组队)
  → 否 → 需多轮协调 / 动态调整?
           → 是 → Swarm 可用? → 是 → Swarm 协作 / 否 → Lead-Member
           → 否 → 标准并行(默认)
```

读者可对话指定("用标准并行" / "策略2")跳过自动选择。**4 策略对照、Swarm 工作流细节见 `reference/orchestration.md`;五模式方法论 + Coordinator Pattern + 数量指南见 `reference/orchestration-patterns.md`**。

## 团队模板与模型速查

4 个模板(full-stack-team / code-review-team / refactor-team / cross-project-fullstack)、模型(opus/sonnet/haiku)、subagent_type(general-purpose/Explore/Plan/code-reviewer):**见 `reference/team-and-registry.md`**。

> 团队自定义 subagent_type(如前端专项)需团队预置;不存在时回退 `general-purpose`。
>
> 完整对话样例:标准并行见 `examples/blueprint-example.md`、Swarm 协作见 `examples/swarm-example.md`、code-review-team(Haiku 资格审 + Sonnet 深审)见 `examples/code-review-example.md`。

## 项目注册表

一次配置多次复用:`.claude/project-registry.json`,[1/6] 自动感知。schema、自动初始化、增量同步:**见 `reference/team-and-registry.md`**。

## 降级规则(环境不全也能跑)

| 场景 | 回退 |
|---|---|
| Swarm 不可用(env var 未设/工具缺失) | 自动回退标准并行,告知用户 |
| devflow skill 未安装 | 跳过集成,走独立模式 |
| 注册表缺失 | [1/6] 扫描兄弟 git 项目自动初始化 → 确认 |
| 自定义 subagent_type 不存在 | 回退 general-purpose |
| Agent 执行失败 | 暂停 → 重试/跳过/终止 |
| 跨项目路径不可达 | 跳过该项目并警告,不影响其他 |
| 全部路径不可达 | 回退单项目模式 + 警告 |

## devflow 集成(可选)

项目装了 devflow skill 时,agent-teams 负责 devflow 的 Stage 4(并行执行),规划(Stage 1-3)和验证归档(Stage 5-6)交接回 devflow。4 种集成模式:**见 `reference/orchestration.md`**。

## 故障处理速查

| 问题 | 处理 |
|---|---|
| Agent 执行失败 | 通知用户,重试/跳过/终止 |
| Skill 找不到 | 回退链:本地 → find-skills → 通用 Agent |
| 质量不达标 | 打回最多 2 轮,仍不过人工介入 |
| 跨项目文件误操作 | prompt 限定路径 + 事后 git diff 检查 |
| 注册表路径不可达 | 跳过该项目并警告 |
| Swarm 不可用 | 自动回退标准 Agent 调度 |

## 更多样例与模式参考

| 文件 | 内容 | 何时读 |
|---|---|---|
| `examples/blueprint-example.md` | 标准并行完整流程(用户认证,含失败重试) | 想看标准并行走法 |
| `examples/swarm-example.md` | Swarm 协作完整生命周期(运营模块,含动态追加任务 / Member 互发消息) | 想看 Swarm 双向协调 |
| `examples/code-review-example.md` | code-review-team 分级审查(Haiku 资格审 + 多 Sonnet 并行深审 + 置信度过滤) | 想看 Coordinator Pattern 落地 |
| `reference/orchestration.md` | 4 策略对照 / Swarm 工作流 / devflow 集成 | 选策略、用 Swarm、接 devflow 时 |
| `reference/orchestration-patterns.md` | 五编排模式 + Coordinator Pattern + 数量指南 + 与四策略映射 | 理解编排原理、决定用不用多 Agent 时 |
| `reference/team-and-registry.md` | 4 模板 + 模型/subagent_type 速查 + 注册表 schema | [2/6] 组团队时 |

---

*Skill v2.2 · 作者 Johnson · 配套手册见 `manual.md` · 细节按需读 `reference/`*
