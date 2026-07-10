# 编排策略与集成(reference)

> 本文件按需读取:SKILL.md 流程中涉及「选策略 / Swarm / devflow 集成」时加载。

## 一、4 种编排策略

| 策略 | 适用 | 怎么做 | 通信 |
|---|---|---|---|
| 直接调用 | 有 Skill 完全覆盖需求 | 直接 `Skill()`,不组队 | — |
| **标准并行(默认)** | 中等/复杂任务,一轮可完成 | 分析→确认→并行派 Agent→验收 | 单向(回主会话) |
| Lead-Member | 需进度跟踪或多轮协调 | Leader 用 TaskCreate/Update 全程跟踪 | 单向 + 任务板 |
| **Swarm 协作** | Swarm 可用 + 多轮动态协调 | TeamCreate + SendMessage 双向 | 双向(Leader↔Member) |

### 自动选择规则

```
任务有 Skill 完全覆盖?
  → 是 → 直接调用
  → 否 → 需多轮协调 / 动态调整(联调、需求会变)?
           → 是 → Swarm 可用(CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)?
                    → 是 → Swarm 协作
                    → 否 → Lead-Member(用 TaskCreate 跟踪)
           → 否 → 标准并行
```

读者可对话指定("用标准并行" / "策略2" / "Swarm")跳过自动选择。

## 二、Swarm 协作模式

### 触发
环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 已设。未设 → 自动回退标准并行,告知用户。

### 与标准并行的区别

| 维度 | 标准并行 | Swarm 协作 |
|---|---|---|
| 通信 | 单向(通知回主会话) | 双向(Leader ↔ Member) |
| 异常处理 | 通知用户决定 | Leader 自主决策 |
| 任务分配 | prompt 内固定 | Leader 动态调整 |
| 适用 | 一轮完成的独立任务 | 多轮协调、动态调整 |

### 工作流

```
[3/6] 确认后:
  TeamCreate("<team-name>")           ← 创建团队
    → Leader Agent(general-purpose / opus)
        - SendMessage 给 Member 分配任务
        - 处理异常、动态追加任务(如联调)
    → Member Agent × N(各 subagent_type)
        - 执行任务、SendMessage 汇报
    → Leader 查 TaskList → 分配下一轮 → 全部完成
  TeamDelete("<team-name>")           ← [6/6] 清理团队资源
```

### Swarm 蓝图格式

```
| # | 角色      | 职责     | 模型   | subagent_type   |
| L | leader    | 协调分配 | opus   | general-purpose |
| 1 | api-dev   | 接口     | sonnet | general-purpose |
| 2 | ui-dev    | 页面     | sonnet | 前端专项(回退 general-purpose) |
```

### Swarm 优势示例
Leader 发现前端需要联调后,动态追加联调任务并通知前端 Agent 执行,**无需中断等待用户决策**。

### Swarm 故障
- Member 无响应:Leader 等待 → SendMessage 确认 → 升级主会话
- Swarm 工具不可用:回退标准并行

## 三、devflow 集成(可选)

> devflow 是教程 `claude-skills` 内的 6 阶段开发流程 skill(编排 OpenSpec + Superpowers)。装了它,agent-teams 可接管其 Stage 4(并行执行)。

### 4 种集成模式

| 模式 | 检测条件 | 行为 |
|---|---|---|
| 独立 | devflow 未安装 | 正常 6 步流程 |
| **devflow 驱动** | devflow 已装 + 无工件 | 逐 Stage 调 brainstorming → openspec-propose → writing-plans 生成规划工件 |
| 完整集成 | devflow 已装 + Plan + specs | 直接从 Plan 按 Capability 生成团队蓝图 |
| 半集成 | devflow 已装 + 只有 specs | 先补 Plan → 再生成蓝图 |

### 分工边界

| 阶段 | 负责方 |
|---|---|
| Stage 1-3(规划) | agent-teams 调 devflow 底层 skill(brainstorming / openspec / writing-plans) |
| Stage 4(执行) | agent-teams 并行 Agent |
| Stage 5-6(验证 + 归档) | 交接回 devflow |

### 安全边界
- 只读 devflow / OpenSpec 工件
- 只写 Plan 的 `### [x]` 标记
- **禁止** git commit(由 devflow 统一管理)

### devflow 模式额外确认点
- 每个 Stage 完成:⚠️ 需要确认 Stage N 完成
- 执行前:🔴 必须确认(同独立模式)
- 完成后:⚠️ 需要确认 devflow 交接

---

*本文件由 SKILL.md 按需加载,不预读。*
