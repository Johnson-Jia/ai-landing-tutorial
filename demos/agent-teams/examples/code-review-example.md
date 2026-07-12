# 团队蓝图示例:code-review-team(分级代码审查)

> ⚠️ **概念性声明**:本样例的 `TeamCreate` / `SendMessage` / `TeamDelete` / `TaskCreate` 等工具名为**概念示意**,用于展示协作模式与分工节奏;实际 API 签名、工具名、参数以 [Claude Code Agent Teams 官方文档](https://docs.claude.com/en/docs/claude-code/agent-teams) 为准(实验功能,可能调整)。

> 场景:对一个有 30+ 改动的 PR 做大规模代码审查。展示**两段式成本/质量权衡**:Haiku 做资格审查(快速过滤无关文件),多个 Sonnet 并行做深度专项审查(安全/性能/可维护性),Haiku 再做置信度聚合,输出红/黄/绿分级报告。
>
> **为什么 Haiku 资格审 + Sonnet 深审**:30 个文件若全用 Sonnet 审,token 成本高且大量时间花在无关紧要的文件(配置、文档、自动生成代码)上。先用便宜的 Haiku 快速过一遍,**只把值得深审的文件交给 Sonnet**——实测能把 Sonnet 的 token 大头砍到 1/3 左右,而质量损失极小(漏审的都是低风险文件)。

## [1/6] 环境检测

```
[1/6] 环境检测
  初始化: ✅
  模式: 独立
  范围: 单项目
  Swarm: ❌ 未启用(标准并行,但本场景一轮完成够用)
```

## [2/6] 团队蓝图(code-review-team)

```
任务目标: 审 PR #xxx(32 文件,+.8k/-1.2k),输出分级审查报告
策略: 标准并行(一轮完成,无需多轮协调)

| # | 角色          | 职责                              | 模型   | subagent_type   | 依赖 | 验收标准                          |
| 1 | screener      | 资格初筛:过滤无关/低风险文件     | haiku  | Explore         | 无   | 给出"深审清单"(N 个文件)+ 理由 |
| 2 | sec-reviewer  | 安全维度深审(注入/越权/密钥)   | sonnet | code-reviewer   | #1   | 高/中风险 finding 各带置信度      |
| 3 | perf-reviewer | 性能维度深审(N+1/锁/慢查询)    | sonnet | code-reviewer   | #1   | 高/中风险 finding 各带置信度      |
| 4 | maint-reviewer| 可维护性深审(命名/重复/耦合)   | sonnet | code-reviewer   | #1   | 高/中风险 finding 各带置信度      |
| 5 | grader        | 聚合 + 置信度过滤 + 分级报告     | haiku  | general-purpose | #2-4 | 报告含红/黄/绿三级 + 阈值过滤记录 |
```

> 模型选择理由:**screener / grader 是 token 大头但判断简单**(过滤、聚合、打分),用 haiku;**深度审查判断复杂**(语义级 bug 识别),用 sonnet。这是 Coordinator Pattern(见 `reference/orchestration-patterns.md`)的最小应用。

## [3/6] 🔴 必须确认

```
> ### 🔴 必须确认:即将执行
> 审查范围: PR #xxx 的 32 个文件改动
> 预计: screener 过滤后约 10-15 文件进入深审,其余标绿(低风险免审)
> 👉 请回复:`确认` 开始执行 | `修改` 调整蓝图
```

用户: `确认`

## [4/6] 并行执行(完整对话 transcript)

### 阶段 A:Haiku 资格审查(screener 先行)

```
🚀 screener 启动中...(Explore / haiku)

screener 扫描 32 个文件,按"是否值得深审"分类:

| 文件                             | 类型      | 行数  | 深审? | 理由                                    |
| README.md                        | 文档      | +120  | ❌ 否 | 文档,无逻辑风险                        |
| package.json                     | 配置      | +3    | ❌ 否 | 依赖版本号,无逻辑                      |
| src/types/generated.ts           | 自动生成  | +450  | ❌ 否 | 自动生成,审了无意义                    |
| src/utils/format.ts              | 工具      | +12   | ❌ 否 | 纯函数,改动小                          |
| src/api/auth.ts                  | 鉴权      | +88   | ✅ 是 | 鉴权逻辑,高风险面                      |
| src/api/user.ts                  | 用户接口  | +120  | ✅ 是 | 涉及用户数据读写                       |
| src/db/query.ts                  | 数据层    | +65   | ✅ 是 | SQL 拼接,注入风险                      |
| src/middleware/rate-limit.ts     | 中间件    | +40   | ✅ 是 | 并发控制,性能/正确性敏感              |
| src/services/order.ts            | 业务      | +200  | ✅ 是 | 核心业务,改动大                        |
| ... (共筛出 12 个文件进入深审)   |           |       |       |                                         |

screener → 主会话:
  深审清单(12 文件): auth.ts / user.ts / query.ts / rate-limit.ts / order.ts / ...
  免审清单(20 文件): 文档/配置/自动生成/纯函数,标 🟢 绿(低风险免审)
```

> **关键决策点 1**:screener 把 32 → 12,后续 3 个 Sonnet 只审这 12 个。**Sonnet token 大头从 32 文件降到 12 文件,约省 60%**。免审文件不丢——它们进最终报告的 🟢 区,有迹可查。

### 阶段 B:多个 Sonnet 并行深审(三个维度并行)

```
🚀 sec-reviewer   启动中...(code-reviewer / sonnet) ← 安全维度
🚀 perf-reviewer  启动中...(code-reviewer / sonnet) ← 性能维度
🚀 maint-reviewer 启动中...(code-reviewer / sonnet) ← 可维护性维度
(三者并行,各自只看自己维度,互不阻塞)
```

**sec-reviewer 的输出(节选)**:

```
sec-reviewer(安全维度)findings:
  [S1] src/api/auth.ts:42  严重程度:高  置信度: 0.92
       JWT 校验未验签算法,攻击者可用 "none" 算法伪造 token
       证据: verify(token, secret) 未传 algorithms: ['HS256']
       建议: 显式指定 algorithms 参数

  [S2] src/db/query.ts:18  严重程度:高  置信度: 0.88
       SQL 字符串拼接,理论注入风险(虽当前输入来自内部)
       证据: `WHERE id IN (${ids.join(',')})`
       建议: 改用参数化查询

  [S3] src/api/user.ts:120 严重程度:中  置信度: 0.65
       用户列表接口未做分页 size 上限,可被一次性拉全量
       建议: size 上限 100
```

**perf-reviewer 的输出(节选)**:

```
perf-reviewer(性能维度)findings:
  [P1] src/services/order.ts:88 严重程度:高 置信度: 0.85
       N+1 查询:循环里调 getUser(id),100 条订单 = 101 次 SQL
       建议: 批量 getUser(ids) 一次查回

  [P2] src/middleware/rate-limit.ts:30 严重程度:中 置信度: 0.55
       限流用内存 Map,多实例部署失效
       建议: 改 Redis
       (注: 单实例部署下不成立,故置信度不高)
```

**maint-reviewer 的输出(节选)**:

```
maint-reviewer(可维护性维度)findings:
  [M1] src/services/order.ts:200-280 严重程度:中 置信度: 0.78
       单函数 80 行,圈复杂度高,5 层嵌套
       建议: 拆 3 个子函数

  [M2] src/api/user.ts vs src/api/order.ts 严重程度:低 置信度: 0.70
       重复的错误响应封装代码(15 行 × 2 处)
       建议: 抽公共工具
```

> **关键决策点 2**:三个 reviewer **并行不阻塞**,各自只盯一个维度,避免一个 reviewer 既看安全又看性能导致 context 散乱。每个 finding **必须带置信度**——为后续 grader 的阈值过滤提供依据。

### 阶段 C:Haiku 聚合 + 置信度过滤 + 分级

```
🚀 grader 启动中...(general-purpose / haiku)
输入: 三个 reviewer 的 findings(共 11 条)+ screener 的免审清单(20 文件)

grader 聚合规则:
  - 置信度 < 0.60 → 过滤(不进报告,但记录"已过滤 N 条低置信度")
  - 红色(🔴 必改): 严重程度=高 且 置信度 ≥ 0.80
  - 黄色(🟡 建议改): 严重程度=中 且 置信度 ≥ 0.60,或 高但置信度 0.60-0.80
  - 绿色(🟢 可不改): 严重程度=低 或 免审文件

已过滤(置信度 < 0.60): 1 条
  - [P2] rate-limit 改 Redis(置信度 0.55,单实例部署下不成立)→ 不进报告主体,只在附录列出
```

## [5/6] 质量验收

```
[5/6] 质量验收(对照 [2/6] 验收标准)
  ✅ screener:      深审清单 12 文件 + 理由齐全
  ✅ sec-reviewer:  高/中风险 finding 各带置信度(3 条)
  ✅ perf-reviewer: 高/中风险 finding 各带置信度(2 条)
  ✅ maint-reviewer:高/中风险 finding 各带置信度(2 条)
  ✅ grader:        分级报告含红/黄/绿 + 阈值过滤记录(过滤 1 条)
```

## [6/6] 结果交付:分级审查报告

```
[6/6] 执行报告 — PR #xxx 分级审查
  审查文件: 32 → 深审 12 → 进报告 8 个 finding(过滤 1 条低置信度)

🔴 必改(2 条 — 高风险且高置信度,合入前必修)
  [S1] auth.ts:42    JWT 未验签算法(置信度 0.92)
  [S2] query.ts:18   SQL 拼接注入风险(置信度 0.88)

🟡 建议改(3 条 — 中风险或中置信度,本 PR 可不合但要跟进)
  [P1] order.ts:88   N+1 查询(置信度 0.85)
  [S3] user.ts:120   分页无上限(置信度 0.65)
  [M1] order.ts:200  函数过长(置信度 0.78)

🟢 可不改(3 条 + 20 免审文件)
  [M2] 重复代码(低风险,后续重构)
  + 20 个免审文件(文档/配置/自动生成/纯函数)

附录:已过滤低置信度(1 条,不进报告主体)
  [P2] rate-limit 改 Redis(置信度 0.55,单实例部署下不成立)

汇总: PR 存在 2 个必改高风险(安全),建议修复后合入
建议: 优先修 S1/S2;P1 性能可在下个迭代;S3 加分页上限成本低可顺手改
```

---

## 附:成本/质量权衡分析

| 维度 | 全 Sonnet 方案 | 本方案(Haiku 资格审 + Sonnet 深审) |
|---|---|---|
| Sonnet 审文件数 | 32 | **12**(过滤掉 20 个低风险) |
| Haiku 审文件数 | 0 | 32(资格审查)+ 11 条 finding 聚合 |
| 估算 token 成本 | 100%(基线) | **约 40%**(Sonnet 大头被砍) |
| 漏审风险 | 0 | 低:免审的是文档/配置/生成代码/纯函数,语义风险极低 |
| 适用场景 | 改动 < 10 文件的小 PR | **改动 > 20 文件的大 PR / 全量审查** |

> **何时反转**:如果 PR 全是核心业务代码(没有文档/配置/生成代码可过滤),Haiku 资格审省不了多少,反而多一道开销——这时直接全 Sonnet 更划算。**本方案的前提是 PR 里有相当比例的"低风险文件"可被 Haiku 过滤掉。**

> **置信度过滤的价值**:不丢掉低置信度 finding(进附录可查),但不让它污染报告主体——避免 reviewer "可能有问题" 的猜测淹没真正的高风险项。阈值 0.60 是经验值,团队可调。

---

*本样例体现 Coordinator Pattern(贵模型规划/判断 + 便宜模型执行 token 大头),模式详解见 `reference/orchestration-patterns.md` §二。code-review-team 模板定义见 `reference/team-and-registry.md`。*
