# 多 Agent 编排模式方法论(reference)

> 本文件按需读取:理解「为什么要这么编排 / 何时用多 Agent / 用几个 subagent / 与本 skill 四策略的关系」时加载。**官方五模式**(Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer)源自 [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents);**Async Multi-Agent / Coordinator Pattern / 数量指南**源自 anthropic-cookbook 的 `patterns/agents/`、`managed_agents/CMA_plan_big_execute_small`、`research_lead_agent.md`。经整理对应到 agent-teams skill。
>
> 配套:`reference/orchestration.md`(本 skill 的 4 策略与 Swarm 工作流)、`reference/team-and-registry.md`(模板与模型速查)。

## 一、Anthropic 五模式 + cookbooks 补充模式

> **来源区分**:① **Anthropic 官方五模式**(出自 [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)):Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer——这是权威的"何时用哪种编排"框架。② **cookbooks 补充模式**(非官方五模式之一,出自 anthropic-cookbook 的 `patterns/agents/` 等示例):Async Multi-Agent——对等通信 / 动态 spawn 的更复杂协作,实务中常用但不在官方五模式枚举内。本文件按官方五模式为主、cookbooks 补充模式为辅,共 6 个。
>
> 选型原则:**先看任务能不能用更简单的模式解决**。Prompt Chaining < Routing < Parallelization < Orchestrator-Workers < Evaluator-Optimizer,复杂度与成本递增。能用流水线就别上多 Agent。

### 1. Prompt Chaining(顺序流水线)

**定义**:把任务拆成线性步骤,前一步输出喂给后一步,每步用独立 prompt。

**示意**:
```
[输入] → [提取] → [转换] → [排序] → [格式化] → [输出]
```

**何时用**:
- 任务能**线性分解**,每步有明确输入输出
- 每步**可靠**(失败率低),不需要回环
- 中间步骤可用代码确定性完成(如排序、格式化)而非 LLM

**典型场景**:数据 ETL(提取 → 清洗 → 排序 → 格式化)、文档翻译(分段 → 翻译 → 合并 → 校对)、报表生成(查询 → 聚合 → 渲染)。

**何时不用**:步骤间有循环依赖、需要回退、或子任务无法预先排序。

### 2. Routing(路由分流)

**定义**:第一个 LLM 做分类,把输入路由到对应的专门 prompt / 处理链。

**示意**:
```
                 ┌→ 技术支持 prompt → 答复
[输入] → 分类器 ─┼→ 账务问题 prompt → 答复
                 └→ 售后服务 prompt → 答复
```

**何时用**:
- 输入有**几类明确的类型**,各自需要不同处理逻辑
- 分类本身简单(LLM 一眼能判),但每类处理复杂
- 各分支相互独立(不需要合并结果)

**典型场景**:客服分流(技术/账务/售后)、邮件分类处理(垃圾/工作/私人→各自处理链)、工单派单(按业务线)。

**何时不用**:分类边界模糊、或各类处理高度重叠(这时合并成一个 prompt 反而更好)。

### 3. Parallelization(并行化)

> **Anthropic 官方五模式之一**。

**定义**:同一 prompt 对**多个输入**并行跑(Sectioning),或**多个不同 prompt** 对同一输入并行跑(Voting),然后聚合。两种变体:
- **Sectioning**:把输入切片成多份,同 prompt 并发处理(如多方干系人分析,每方一段)
- **Voting**:多个 prompt 各自评一遍同一输入,投票/取众数(如多评审员独立打分后聚合)

**示意**:
```
Sectioning(同 prompt × 多输入):       Voting(多 prompt × 同输入):
  ┌→ prompt A(输入 1)┐                   ┌→ prompt 甲 → 评 1┐
  ├→ prompt A(输入 2)┼→ 聚合             ├→ prompt 乙 → 评 2┼→ 投票/聚合
  └→ prompt A(输入 3)┘                   └→ prompt 丙 → 评 3┘
```

**何时用**:
- 子任务**相互独立、可同时跑**,且整体时间 = max(子任务) 而非 sum
- 拆分方式**预先知道**(不用看输入才决定拆几个)
- 想要**多视角/多评审员**降低单次判断的方差

**典型场景**:多方干系人影响分析(同 prompt 跑产品方/技术方/运营方视角)、多评审员独立打分后投票、长文档按章节并行摘要(再合并)。

**与 Orchestrator-Workers 的区别**:Parallelization 的并行度与子任务**预先固定**(已知拆几个、各自跑什么);Orchestrator-Workers 的子任务**运行时才由 orchestrator 决定**拆几个。

### 4. Orchestrator-Workers(编排者 + 工作者)

**定义**:Orchestrator 在**运行时**动态决定拆成哪些子任务,然后并行派给 worker,最后汇总。

**示意**:
```
                  ┌→ worker A(子任务 1)┐
[输入] → orchestrator ─→ worker B(子任务 2)┼→ orchestrator 汇总 → [输出]
                  └→ worker C(子任务 3)┘
       (子任务列表运行时生成,非预定义)
```

**何时用**:
- 子任务**无法预定义**——要看了输入才知道拆成几个
- 子任务间**相互独立**,可并行
- 需要一个"大脑"做拆分决策和结果合成

**典型场景**:营销文案多视角生成(看完产品后,决定从痛点/数据/故事/对比几个角度并行写)、代码库全景调研(看完项目后,决定拆成几个模块分别分析)、长文档摘要(看完结构后,决定按章节并行摘要)。

**与 Prompt Chaining 的区别**:Chaining 的步骤是**预先固定的顺序**;Orchestrator-Workers 的子任务是**运行时动态生成**的并行集合。

### 5. Evaluator-Optimizer(生成-评估循环)

**定义**:Generator 出初版 → Evaluator 按标准打分 → 不达标则带反馈回 Generator → 循环直到 PASS 或达轮数上限。

**示意**:
```
         ┌─────────────────────────────────┐
         ↓                                 │
[输入] → generator → 产物 → evaluator → PASS? ─YES→ [输出]
                                  │NO
                                  └→ 反馈 → (回 generator)
```

**何时用**:
- 有**明确的评价标准**(可机器判定的 PASS/FAIL)
- 初版**常常不达标**(否则单次生成就够,不用循环)
- 每轮反馈能让 generator 真的改进(而不是反复犯同样错)

**典型场景**:代码质量迭代(生成 → 跑测试/静态检查 → 改 → 再测)、翻译校对(翻 → 对照术语表 → 改)、SQL 优化(生成 → EXPLAIN → 改)。

**何时不用**:没有客观评价标准(纯主观偏好,循环无意义)、或单次生成已足够好(白白多花 token)。

### 6. Async Multi-Agent(异步多 Agent 协作)

> ⚠️ **cookbooks 补充模式,非 Anthropic 官方五模式之一**——出自 anthropic-cookbook 的 `patterns/agents/` 等示例。官方五模式(Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer)更基础,Async Multi-Agent 在其之上更复杂、实务中也常用,但不在官方枚举内。

**定义**:多个对等 Agent(peer-to-peer)协作,或一个 lead Agent 动态 spawn 子 agent。通信方式两种:
- **对等 peer**:固定 N 个 agent,各自有角色,互相通信
- **动态 spawn**:lead 看运行时情况,临时拉起 subagent 做子任务

**示意**:
```
对等 peer(固定团队):              动态 spawn(lead 拉子 agent):
  agent A ←──→ agent B               lead ──spawn→ subagent 1
    ↑          ↑                     lead ──spawn→ subagent 2(看完 1 才拉)
    └──→ agent C                     lead ←─汇总── subagent × N
```

**何时用**:
- 任务需要**多角色协作**(各角色有不同专长与上下文)
- 或子任务**运行时才知道**(无法预先规划,要看了中间结果决定下一步)
- 通信频繁、需要动态调整

**典型场景**:复杂软件项目开发(架构/前端/后端/测试协作)、深度调研(lead 看到第一轮结果才知道要深挖哪个方向)、Swarm 模式下的团队协作。

**与其他模式的区别**:Async Multi-Agent 强调**对等通信**与**动态 spawn**,比 Orchestrator-Workers 的"一次拆分 + 汇总"更复杂——Agent 间有多轮往返。

---

### 模式速查对照(Anthropic 五模式 + cookbooks 补充)

| # | 模式 | 来源 | 拓扑 | 子任务预定义? | 通信 | 典型场景 |
|---|---|---|---|---|---|---|
| 1 | Prompt Chaining | 官方 | 线性 | ✅ 固定顺序 | 单向(前→后) | ETL、流水线 |
| 2 | Routing | 官方 | 分叉 | ✅ 固定分支 | 单向(分类→分支) | 客服分流 |
| 3 | Parallelization | 官方 | 扇出→聚合 | ✅ 固定并发度 | 单向(派/收) | 多视角/多评审 |
| 4 | Orchestrator-Workers | 官方 | 一对多一 | ❌ 运行时拆 | 双向(派/收) | 动态拆分并行 |
| 5 | Evaluator-Optimizer | 官方 | 循环 | ✅ 固定两角色 | 双向(反馈) | 质量迭代 |
| 6 | Async Multi-Agent | cookbooks 补充 | 网状 | ❌ 动态 | 多向(peer/spawn) | 多角色协作 |

---

## 二、Coordinator Pattern(贵模型规划 + 便宜模型执行)

> 源自 Anthropic cookbooks `managed_agents/CMA_plan_big_execute_small`(Coordinator-Managed Agents: plan big, execute small)。

### 思路

把任务分成两类工作:
- **规划 + 综合(key decision)**:关键决策、跨子任务综合、最终质量把关——交给贵模型(Opus / Sonnet)。
- **执行(token 密集但判断简单)**:搜索、读取、过滤、打分、格式化——交给便宜模型(Haiku)。

```
[任务] → Coordinator(Opus/Sonnet)
            ├─ 规划:拆子任务、给每个子任务的具体指令
            ├─ 派给 → Executor × N(Haiku)做 token 大头
            ├─ 收回 → 必要时再派下一轮
            └─ 综合:跨结果合成最终输出 + 质量把关
```

### 为什么有效

LLM 调用的 token 成本结构:**执行类(读取/搜索)产生海量 token,但每个 token 的判断密度低**;**规划/综合类 token 少,但每个 token 的判断密度高**。把前者下放给便宜模型,后者留给贵模型——总成本能显著下降,而关键决策质量不降。

### 经济性验证思路(rigor-matched 控制组)

要量化降本幅度,设两个严格可比的组:

| 维度 | 控制组 | 实验组(Coordinator) |
|---|---|---|
| 任务集 | 同一批任务 | 同一批任务 |
| 总 token | 记录 | 记录 |
| 贵模型 token | 100%(全程贵模型) | 仅规划/综合部分 |
| 便宜模型 token | 0% | 执行部分 |
| **输出质量** | 用统一 rubric 打分 | 用同一 rubric 打分 |
| **总成本** | 基线 | 对比 |

**关键**:质量不能掉——若便宜模型执行导致质量明显下降,则"省的钱"是假阳性。只有质量持平(或可接受的微小下降)且成本下降,模式才成立。

> 本 skill 的 `code-review-team` 就是 Coordinator Pattern 的最小落地:screener/grader 用 haiku(执行 token 大头),sec/perf/maint-reviewer 用 sonnet(关键判断)。样例见 `examples/code-review-example.md`。

---

## 三、编排决策方法论(用不用多 Agent / 用几个)

> 源自 Anthropic cookbooks `research_lead_agent.md`——一个做深度调研的 lead agent,核心方法论是「按任务复杂度决定 spawn 几个 subagent、用什么 spawn 策略」。

### A. 何时用多 Agent(避免过度编排)

**第一原则**:能单 Agent 解决就别多 Agent。多 Agent 的成本(通信开销、协调复杂度、调试难度)只有任务足够复杂时才值。

判断流程:
```
任务是不是单步直答(一次搜索/一次推理就能给答案)?
  → 是 → 单 Agent,别编排
  → 否 → 任务是否多源/多步/多角色?
           → 是 → 考虑多 Agent(再看下面 B 决定用几个)
           → 否 → 单 Agent + 多轮 tool 调用即可
```

**过度编排的反模式**:
- 把"读一个文件回答问题"拆成「explorer + reader + summarizer」3 个 agent——纯增加协调成本,无收益
- 用 Evaluator-Optimizer 但没有客观标准——循环无意义
- 用 Swarm 但任务一轮就能完成——Leader 形同虚设

### B. 用几个 subagent(复杂度 → 数量映射)

任务复杂度大致映射到 subagent 数量:

| 任务复杂度 | 典型特征 | subagent 数量 |
|---|---|---|
| **简单** | 单点查询、单一来源 | **1 个**(直接调用,不组队) |
| **标准** | 明确多步,各步独立 | **2-3 个** |
| **中等** | 多源整合,需交叉验证 | **3-5 个** |
| **复杂** | 全景调研、跨多模块/多项目 | **5-10 个** |
| **上限** | 超大规模(罕见) | **≤ 20 个**(超过则拆任务,非堆 agent) |

**上限原则**:**超过 20 个 subagent 通常意味着任务本身该拆成多次会话**,而不是在一个会话里堆更多 agent。协调成本随 agent 数超线性增长——20 个 agent 的协调开销往往吞掉并行带来的收益。

> "堆 agent 不等于更强"——若 N 个 agent 质量不达标,先看是不是任务拆分有问题、prompt 不够明确,而不是直接加到 2N 个。

### C. 查询类型分层(决定 spawn 策略)

lead agent 根据查询类型选不同 spawn 策略:

| 查询类型 | 特征 | spawn 策略 |
|---|---|---|
| **depth-first(深挖单点)** | 围绕一个具体问题深挖到底 | 少量 agent,每个跑长 tool chain;不并行扩宽 |
| **breadth-first(广扫多源)** | 横扫多个独立来源整合 | 多 agent 并行,每个负责一源;汇总合成 |
| **straightforward(直答)** | 单步可答 | 不 spawn,lead 直接用 tool 答 |

**lead 的决策逻辑**:
```
看到查询 → 判类型:
  straightforward → 自己答,不 spawn
  depth-first    → spawn 1-2 个深度 agent
  breadth-first  → 按"覆盖范围"决定并行数(3-10 个)
```

> 这与「数量映射」叠加:复杂度决定总数,查询类型决定并行 vs 深度的分布。

---

## 四、与本 skill 四策略的关系(映射表)

本 agent-teams skill 的「直接调用 / 标准并行 / Lead-Member / Swarm」四策略,分别对应上述哪些模式:

| 本 skill 策略 | 对应的编排模式 | 说明 |
|---|---|---|
| **直接调用** | (单 Agent,不编排) | 任务有 Skill 完全覆盖,直接 `Skill()` 调用,等于"straightforward 查询不 spawn" |
| **标准并行** | Orchestrator-Workers(简化版) | 主会话做 orchestrator,拆固定子任务并行派 Agent,结果汇总。**子任务预定义**(蓝图阶段写死) |
| **Lead-Member** | Orchestrator-Workers + 轻量 Coordinator | Leader 用 TaskCreate 全程跟踪(规划 + 综合),Member 执行。比标准并行多了进度跟踪和多轮能力 |
| **Swarm 协作** | Async Multi-Agent(对等 peer) | TeamCreate 后 Leader ↔ Member 双向通信,Member 间也可互发消息。**动态协调、动态追加任务** |

**对应的模式未直接落地为独立策略,但在 skill 内部被组合使用**:

| 模式 | 在本 skill 哪里体现 |
|---|---|
| Prompt Chaining | [1/6]→[2/6]→...→[6/6] 本身就是固定顺序的 6 步流水线(skill 内部用代码串联,非 LLM 串联) |
| Routing | 没有显式策略,但 [2/6] 选模板时("这是审查任务 → code-review-team")是一种轻量 routing |
| Parallelization | [4/6] 无依赖的子任务并发派多个 Agent(同 prompt × 多子任务),即 Sectioning 变体;多 reviewer 并行审不同维度近 Voting |
| Evaluator-Optimizer | [5/6] 质量验收不通过 → 打回 Agent 重做(最多 2 轮),是 Evaluator-Optimizer 的有限轮实现 |
| Coordinator Pattern | code-review-team 的 screener/grader(haiku)+ reviewer(sonnet)分工;Leader 用 opus、Member 用 sonnet/haiku 的模型分层 |

### 什么时候用哪个策略(决策速查)

```
你的任务有现成 Skill 完全覆盖?
  → 是 → 直接调用(= 单 Agent,不编排)
  → 否 → 任务能一轮完成(子任务预定义、无多轮协调)?
           → 是 → 标准并行(= Orchestrator-Workers 简化版)
           → 否 → 需多轮协调 / 进度跟踪,但 Member 间无需互发消息?
                    → 是 → Lead-Member(= Orchestrator-Workers + 跟踪)
                    → 否 → 需 Member 间对等通信 / 动态追加任务 + Swarm 可用?
                             → 是 → Swarm 协作(= Async Multi-Agent)
                             → 否 → Swarm 不可用 → 回退 Lead-Member
```

> 决策原则:**从最简单的策略开始,只在不够用时升级**。Swarm 不是"高级"选项,而是"任务确实需要动态协调时才用"的选项——它的协调成本(Leader 全程 opus 在线、双向通信开销)只有在多轮协调需求确实存在时才回本。

---

*本文件由 SKILL.md / manual.md 按需加载,不预读。官方五模式源自 [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents),Async Multi-Agent / Coordinator Pattern 源自 anthropic-cookbook,经整理对应到本 skill。*
