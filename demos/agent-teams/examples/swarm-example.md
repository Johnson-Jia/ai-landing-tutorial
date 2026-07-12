# 团队蓝图示例:Swarm 协作(多轮动态协调)

> ⚠️ **概念性声明**:本样例的 `TeamCreate` / `SendMessage` / `TeamDelete` 等工具名为**概念示意**,用于展示协作模式与交互节奏;实际 API 签名、工具名、参数以 [Claude Code Agent Teams 官方文档](https://docs.claude.com/en/docs/claude-code/agent-teams) 为准(实验功能,可能调整)。

> 场景:开发一个后台运营模块(CRUD + 报表 + 数据导出),前后端要联调、需求会在过程中微调。Swarm 可用(`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)。展示完整生命周期:`TeamCreate` → 分派 → 协调 → 验收 → `TeamDelete`。
>
> **为什么用 Swarm 而不是标准并行**:任务不能一轮写死——前端要等后端接口稳定才能联调,联调中又可能暴露接口缺口,需要 Leader 在运行时动态追加任务、协调多角色,而不是中断等用户决策。

## [1/6] 环境检测

```
[1/6] 环境检测
  初始化: ✅
  模式: 独立
  范围: 单项目
  注册表: 已加载(1 个项目)
  Swarm: ✅ 可用(CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)
```

## [2/6] 团队蓝图(Swarm 协作)

```
任务目标: 运营后台模块 = CRUD 管理 + 数据报表 + 数据导出,前后端联调
策略: Swarm 协作(多轮协调 + 动态调整需求 + Swarm 可用)

| #   | 角色        | 职责                       | 模型   | subagent_type   | 依赖     | 验收标准                          |
| L   | leader      | 协调分配 / 异常处理 / 联调  | opus   | general-purpose | —        | 全部子任务完成 + 联调通过          |
| 1   | api-dev     | CRUD 接口 + 数据模型       | sonnet | general-purpose | L        | CRUD 接口齐,单测通过              |
| 2   | report-dev  | 报表查询 + 聚合            | sonnet | general-purpose | L        | 报表口径正确,返回 < 2s            |
| 3   | export-dev  | 导出(Excel/CSV)          | sonnet | general-purpose | L        | 大数据量导出不超时,文件可打开     |
| 4   | frontend    | 管理页 + 联调              | sonnet | 前端专项        | L,#1     | 4 个页面联通接口,可演示           |
```

> Swarm 蓝图只列**首派角色**——Leader 会在运行时根据情况追加(如联调 fixer、口径对齐 reviewer)。

## [3/6] 🔴 必须确认

```
> ### 🔴 必须确认:即将执行(Swarm 模式)
> Leader 将自主协调任务分配和异常处理,包括:
>   - 动态追加联调、口径对齐等子任务
>   - Member 失败时 Leader 自主重试或重新分配
>   - 仅 Leader 无法决策时才升级主会话
> 👉 请回复:`确认` 开始执行 | `修改` 调整蓝图
```

用户: `确认`

## [4/6] Swarm 执行(完整对话 transcript)

### 阶段 A:建队 + 首派

```
🏗️ TeamCreate("ops-module")  ← 创建团队
✅ 团队已创建,Leader = leader(opus / general-purpose)

leader (SendMessage → api-dev):
  任务: 实现 CRUD 接口(运营记录:列表/详情/新增/编辑/删除)
  数据模型: t_ops_record(rec_id, biz_type, status, owner, amount, created_at)
  先出接口约定(返回给 frontend 同步)

leader (SendMessage → report-dev):
  任务: 报表查询 — 按 biz_type 聚合 amount,支持按月/按周维度
  数据口径: amount 为含税金额;状态排除 "草稿"

leader (SendMessage → export-dev):
  任务: 导出 — 支持按当前筛选条件导出 Excel/CSV
  约束: 单次导出 > 5w 行时走异步任务

leader (SendMessage → frontend):
  任务: 4 个管理页(列表/详情/新增编辑/报表)
  等待 api-dev 给出接口约定后开工
```

### 阶段 B:并行执行 + Member 互发消息协调

```
api-dev (SendMessage → frontend):
  接口约定已就绪(贴在共享 doc):
    GET /api/ops/records?biz_type=&page=&size=
    GET /api/ops/records/{rec_id}
    POST /api/ops/records
    PUT  /api/ops/records/{rec_id}
    DELETE /api/ops/records/{rec_id}
  字段见 doc,字段命名 camelCase,你按这个开工

frontend (SendMessage → api-dev):
  收到。注意:列表页要显示 owner 中文名,接口能不能 join 用户表带回来?
  不然我要二次请求用户接口,列表慢。

api-dev (SendMessage → frontend):
  有理,改成列表接口直接带 owner_name。

report-dev (SendMessage → leader):
  口径确认:报表的"按周"是自然周(周一-周日)还是滚动 7 天?
  需求没写明。

leader (SendMessage → report-dev):
  自然周(周一-周日)。在报表说明里标注口径,避免歧义。
```

> **关键决策点 1**:Member 间直接对话(api-dev ↔ frontend)解决字段问题,**没打扰 Leader**,Leader 只在需要拍板时介入(report-dev 的口径疑问)。这是 Swarm 的核心优势——对等通信降低 Leader 瓶颈。

### 阶段 C:Leader 发现新需求 → 动态追加任务

```
export-dev (SendMessage → leader):
  异步导出任务需要一个任务表 + 状态查询接口,设计如下:
    t_export_task(task_id, user_id, status, file_url, created_at)
  这个不在原任务里,是否要做?

leader:
  [决策] 需要。这是导出功能完整闭环的一部分,属于隐含依赖。
  → 动态追加任务 #5

leader (SendMessage → export-dev):
  追加任务 #5:实现导出任务表 + 状态查询接口(GET /api/ops/export/tasks/{task_id})
  与 #3 同一 Agent 做(你最熟上下文)

export-dev: 收到,#3 + #5 一起做。
```

> **关键决策点 2**:Leader **没中断问用户**,自主判断"异步任务表是导出功能的必要组成"并追加。标准并行模式这里只能暂停等用户,Swarm 直接消化。

### 阶段 D:进度跟踪 + 异常处理

```
leader (查 TaskList):
  #1 api-dev      ✅ CRUD 接口完成(单测通过)
  #2 report-dev   ⏳ 报表查询开发中
  #3 export-dev   ⏳ #3 + #5 并行开发中
  #4 frontend     ⏳ 4 个页面开发中(已对齐接口)
  #5 export-task  ⏼ 等待 export-dev

report-dev (SendMessage → leader):
  ❌ 报表慢查询:按 biz_type 聚合 + 排除草稿,3 个月数据要 6s,远超 2s 验收标准。
  已有索引 (biz_type, status),不够。

leader (SendMessage → report-dev):
  [决策] 加 (biz_type, status, created_at) 复合索引,created_at 走范围扫。
  数据量预估 < 100w,够用。先 EXPLAIN 验证再上。

report-dev (SendMessage → leader):
  EXPLAIN 走索引,3 个月数据 0.8s。已加索引,报表 < 1s。✅
```

> **关键决策点 3**:Member 失败/卡壳时,**Leader 自主给方案**而不是甩给用户。只有当 Leader 也没把握(如改表结构影响线上)才升级主会话。

### 阶段 E:联调 → 全员完成

```
api-dev (SendMessage → frontend): 接口已部署到联调环境,可以联调
frontend (SendMessage → leader):
  联调 3/4 页面通过。报表页报错:接口返回 amount 是分,前端按元显示,差 100 倍。

leader (SendMessage → frontend):
  立即修复:前端做 /100 转换,统一显示元。
leader (SendMessage → report-dev):
  记账:接口文档注明 amount 单位是分(避免后续踩坑)。

frontend (SendMessage → leader): 报表页修复,4/4 联调通过 ✅

leader (查 TaskList): 全部 ✅
```

## [5/6] 质量验收

```
[5/6] 质量验收(对照 [2/6] 验收标准 + 动态追加 #5)
  ✅ api-dev:     CRUD 接口齐,单测通过
  ✅ report-dev:  报表口径正确(自然周),返回 < 1s(< 2s 标准)
  ✅ export-dev:  导出 + 异步任务表闭环,5w 行不超时
  ✅ frontend:    4 个页面联调通过,可演示
  ✅ leader:      全部子任务完成 + 联调通过(含 1 个动态追加任务)
```

## [6/6] 结果交付

```
[6/6] 执行报告
  成功: 5/5(+1 动态追加) | 失败: 0/5
  ✅ api-dev:     CRUD 接口 + 单测(8 个文件)
  ✅ report-dev:  报表查询 + 复合索引(5 个文件)
  ✅ export-dev:  导出 + 异步任务表(6 个文件)
  ✅ frontend:    4 个管理页(9 个文件)
  汇总: 运营后台模块已实现,前后端联调通过,口径对齐
  建议: 上线前压测报表大数据量;前端可加导出进度条
  🧹 Swarm 清理: TeamDelete("ops-module")  ← 销毁团队资源
```

---

## 附:Swarm 与标准并行的关键差异(本样例体现)

| 时刻 | 标准并行会怎样 | Swarm 实际做的 |
|---|---|---|
| api-dev ↔ frontend 字段对齐 | 各自回主会话,用户协调 | **Member 直接对话**解决 |
| report-dev 口径疑问 | 暂停问用户 | **Leader 拍板**(自然周) |
| 发现异步任务表缺失 | 暂停问用户要不要做 | **Leader 自主追加任务 #5** |
| 报表慢查询不达标 | 打回 + 通知用户 | **Leader 给索引方案**,Member 验证 |
| 联调单位不一致 | 暂停问用户 | **Leader 双向调度**,记账防再踩 |

> 结论:Swarm 把 N 个"本该暂停等用户"的时刻,降到 0(本例)。Leader 自主消化动态协调,Member 间对等通信降低 Leader 瓶颈。代价:Leader 用 opus + 全程在线,token 成本高于标准并行——**只用在确有多轮协调需求时**。

---

*本样例与 `blueprint-example.md`(标准并行)对照阅读。Swarm 工作流细节见 `reference/orchestration.md` §二。*
