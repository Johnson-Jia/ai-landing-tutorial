# Claude Code + Skill 实战心法

> Claude Code + Skill 实战心法，作为本目录 [README](./README.md) 的补充——README 讲「skill 仓库怎么用」，这里讲「Claude Code 怎么用得顺手、skill 怎么写得值钱」。
>
> 不是金科玉律，是一般情况下有效的起点。用久了你会长出自己的直觉。

---

## 一、Claude Code 最佳实践心法

围绕一个核心约束展开：**Claude 的上下文窗口（约 200K 词元）会快速填满，填满后性能下降。** 几乎所有心法都在和这个约束博弈。

### 1. 验证驱动：给它验证手段，别只信任输出

这是提升质量最有效的单一策略。没有验证手段时，Claude 会产出**看起来对但实际跑不起来**的代码，而你成了唯一的反馈回路。

- **给它验证工具**：把测试命令、lint 脚本、截图能力都交给它。
- **让它自己跑验证**：别只说「确保正确」，要说「运行 `npm test` 确认」。
- **无法验证就别发布**：这是底线。
- **把验证固化**：测试命令写进 CLAUDE.md；用 Hooks 在每次文件编辑后自动跑 lint/格式化；在 skill 末尾强制加一步验证。

> 一句话：验证 > 信任。

### 2. Plan Mode 是基础操作，不是可选步骤

让 Claude 直接跳到编码，可能产出**解决错误问题**的代码。推荐四阶段：**探索 → 计划 → 编码 → 提交**。

- **探索**用 Plan Mode（只读，不动文件），理解代码结构和现有模式。
- **计划**也在 Plan Mode 里做，按 `Ctrl+G` 在编辑器里改计划，删掉不想要的步骤。
- 复杂任务可以开**第二个 Claude 会话**审计这个计划——挑遗漏的边界情况、潜在问题、更好的替代方案。新上下文的审查更客观，因为另一个 Claude 不会偏向它自己刚写的代码。
- **经验法则**：不确定方案、改动跨多文件、对代码不熟 → 用 Plan Mode。改个错别字、加一行日志 → 直接动手。

### 3. 上下文是最贵的资源：`/clear` 是你最好的朋友

- **及早纠正**：如果你已经修正 Claude 两次，上下文已经被失败方案污染了。`/clear` 重开，用融合了前两轮教训的更好提示词——**干净会话 + 好提示词，几乎总是优于长会话 + 反复修正**。
- **厨房水槽式会话是大忌**：一个会话里塞多个不相关任务，上下文全是噪声。任务切换之间 `/clear`。
- **别无限探索**：「调查一下这个问题」不限范围，它能读上百个文件把上下文撑爆。缩小范围（「只看 src/auth/ 目录」），或者用子代理去探索，只把摘要带回主会话。
- **`/context`** 看消耗分布，**`/compact`** 带指令手动压缩（如 `/compact 聚焦 API 变更和测试结果`）。

### 4. 子代理是你的上下文防火墙

子代理运行在**独立的上下文窗口**里，有自己的系统提示和工具权限。它去探索代码库、读文件，**只返回摘要到主会话**，不污染主上下文。

- **隔离探索**：不熟悉的大段代码、跨多文件调研 → 丢给子代理。
- **并行处理**：Writer/Reviewer 模式——一个会话写代码，另一个独立会话审查；或一个写测试、另一个写实现让测试通过。
- **`/btw` 是子代理的逆操作**：「有上下文但没工具」——问它「刚才那个配置文件叫什么来着」，它能看当前会话但不能读文件。

### 5. 五件套辨析：CLAUDE.md / Skills / Sub-agents / Hooks / MCP

理解这五个扩展机制的区别，是高效配置环境的关键。别一锅炖。

| 机制 | 定位 | 加载方式 | 适合什么 |
|---|---|---|---|
| **CLAUDE.md / rules/** | 团队规范 | 每次会话全量加载 / 按路径匹配 | 所有开发者必须遵守的规则 |
| **Skills** | 领域知识 + 工作流 | description 常驻，正文按需加载 | 每天做超过一次的重复工作流 |
| **Sub-agents** | 独立上下文里的专家 | 独立上下文窗口 | 隔离探索、并行处理 |
| **Hooks** | 确定性保证 | 工作流节点自动触发 | 必须自动执行的操作（格式化、保护文件） |
| **MCP** | 外部数据源连接 | 连接时加载 | 连数据库、Notion、Figma 等 |

三个易混的辨析：
- **Slash Commands vs Skills vs Sub-agents**：快捷指令（继承主会话上下文）/ 领域知识+工作流（description 常驻 + 按需加载）/ 独立上下文中的专家。
- **CLAUDE.md vs Hooks**：CLAUDE.md 是建议性的（Claude 可能忽略）；Hooks 是确定性的（一定执行）。需要保证发生的操作（格式化、阻止编辑受保护文件）→ 用 Hooks。
- **CLI vs MCP**：能用 `gh`、`aws`、`gcloud` 完成的，优先用 CLI——CLI 无常驻上下文成本，只在调用时产生输出；MCP 服务器的工具定义默认常驻占上下文。

### 6. 配置是长期杠杆：投入一次，每次会话都回报

- **CLAUDE.md 检验标准**：对每一行问「删掉它，Claude 会犯错吗？」不会就删。臃肿的 CLAUDE.md 会让它忽略真正重要的指令。
- **预批准而非跳过权限**：用 `/permissions` 把安全的常用命令（lint、test、git）加白名单，而不是用 `--dangerously-skip-permissions` 关掉所有权限门。前者是有意识的安全决策，后者是拆掉安全门。
- **分层配置**：企业策略 > 用户级 > 项目级 > 默认。更具体的优先。子目录的 CLAUDE.md 按需加载（访问到那个目录才加载）。
- **犯错后更新规则**：Claude 每犯一个错，都是改进 CLAUDE.md 的机会——「刚才那个错是因为 X，更新 CLAUDE.md 加规则防止类似情况」，形成自我改进循环。

### 7. Headless 模式：把 Claude 变成可编程函数

`claude -p` 让 Claude 在任何无交互环境里跑——CI 管道、pre-commit hook、自动化脚本、定时任务。本质是 `f(输入) → 输出`。

```bash
# 管道输入
cat error.log | claude -p "简洁地解释这个构建错误的根因"
git diff main | claude -p "审查这些变更中的安全问题"

# JSON 输出 + 权限控制 + 系统提示定制
git diff main...HEAD | claude -p "Review this PR diff" \
  --output-format json \
  --allowedTools "Edit,Bash(npm run lint)" \
  --append-system-prompt "Focus on security vulnerabilities."
```

**Fan-out 批量处理**：大规模迁移时，先生成任务列表，再循环并行调用，每个任务一个独立 PR。最佳实践——**先在 2-3 个文件上测试、优化提示词，再批量执行**。

### 8. 多会话并行：一个人当一个团队用

当你用好了一个 Claude，用并行倍增产出。三种方式：多个终端窗口 / Desktop 多窗口 / Git Worktrees（每个会话一个独立工作目录，互不干扰）。

- **Worktree 并行**：`claude --worktree feature-auth`、`claude --worktree bugfix-123` 各开一个，独立工作目录，互不干扰。
- **并行不只是加速**：新上下文让代码审查更客观。
- **长时间任务别被权限阻塞**：日常用 `/permissions` 预批准；隔离环境才用 `--dangerously-skip-permissions`。

---

## 二、Skill 编写与管理方法论

### 1. skill.md 怎么写：三件套结构

一个 skill = `SKILL.md`（入口）+ `reference/scripts`（按需加载）+ 可选 `rules/<name>.md`（覆盖规则）。

```markdown
---
name: fix-issue
description: 修复 GitHub Issue（写清「何时触发」，因为 frontmatter 常驻上下文）
disable-model-invocation: true   # 可选：禁止模型自动调用，只能 /fix-issue 显式触发
---
分析并修复 GitHub Issue: $ARGUMENTS。

1. 使用 gh issue view 获取 Issue 详情
2. 搜索代码库找到相关文件
3. 实现修改
4. 编写并运行测试验证修复   ← 末尾强制一步验证
5. 创建描述性的提交消息并创建 PR
```

**两个要点**：
- **frontmatter 的 description 决定生死**：它常驻上下文（约占预算 2%），模型靠它判断「该不该触发这个 skill」。description 写不清「何时触发」，skill 就形同虚设。
- **正文要精简**：详细内容拆到 `reference.md` 或 `scripts/`，按需读取。

### 2. 渐进式披露：三层加载，省词元

skill 采用三层加载，是它比 CLAUDE.md 全量常驻更省的关键：

| 层级 | 内容 | 加载时机 | 词元消耗 |
|---|---|---|---|
| **元数据层** | 所有 skill 的 name + description | 始终加载 | 极低（轻量目录） |
| **指令层** | SKILL.md 正文（触发逻辑、流程） | 选中后才加载 | 中等 |
| **资源层** | Reference 文件（被读取）/ Script 脚本（被执行） | 需要时才触发 | Reference 按文件大小 / Script 几乎为零 |

**Reference vs Script 怎么选**：
- **Reference**（被读取）：适合中大型文档、查询资料、规则验证。模型会读它的内容。
- **Script**（被执行）：适合轻量级代码运行、文件操作。模型只调用、不读内容——所以脚本里塞密钥/Token 不会进上下文，更安全。

### 3. 写好 skill 的四个关键

- **编排不实现**：能调底层 skill / 框架就调，不重造轮子。一个 skill 可以只是「把几个现成能力串起来」。
- **渐进式披露**：SKILL.md 精简到只放触发逻辑和路由，详细内容拆到子文件按需读（比如长流程的每个阶段各一个文件）。
- **恢复判定**：长流程要有「中断后从哪继续」的逻辑——查文件状态判断恢复点，而不是从头再来。
- **覆盖规则**：`rules/<name>.md` 始终生效，用来改写底层 skill 的默认出口 / 边界（比如把 commit 动作统一收口到某个阶段）。

### 4. 命名空间与生命周期组织

- **目录即命名空间**：一个 skill 自包含一个目录（kebab-case，如 `sql-query/`），目录里放 SKILL.md + reference + scripts。
- **分层放置**：`~/.claude/skills/` 用户级（跨项目复用）；项目 `.claude/skills/` 项目级（团队共享，提交 Git）。
- **团队 Skill 仓库**：用统一的 `.claude/` 布局把一组 skill 组织起来，整个目录可独立打包分发——这是团队沉淀复用的载体。
- **生命周期**：从「个人一次性脚本」→「个人 skill」→「团队 skill 仓库」→「脱敏通用化对外发布」。每次升级都是把上下文里的隐性知识固化成可复用资产。

### 5. 装 skill 前先过安全审核

skill 可以包含可执行脚本，下载来源不明的 skill 等于让别人在你机器上跑代码。**装之前先审**：
- 看 SKILL.md 的 frontmatter 和正文，确认触发条件和指令透明。
- 重点查 scripts/ 里的脚本：有没有外发数据、有没有危险命令、有没有硬编码凭证。
- 社区有专门的「skill-vetter」类工具，用 AI 代理对 skill 做安全审核后再安装。
- 团队内部应有审核流程：个人写的 skill 进团队仓库前，由另一位成员过一遍。

---

## 三、多 Agent 实战避坑

把多个 Claude 塞进一个团队并行干活很爽，但坑也不少。以下来自多端并行项目实战。

### 1. 数量稳妥起见 2-3 个，别一上来就开 5 个

- **资源是硬约束**：多个 agent 同时跑，内存/CPU 容易撑爆，Windows 下尤其容易出现 fork 失败（`Resource temporarily unavailable`）。
- **2-3 个最稳**：先从 2-3 个 agent 起步，验证流程跑通后再扩。减少同时数量、用更轻的模型（haiku/sonnet）都能降压。
- **角色分工要清晰**：比如 1 个分析（产出接口契约/需求文档）+ 2-3 个开发（各负责一端）。分析阶段其他 agent 阻塞等待，契约出来后再并行开发——别让所有 agent 一窝蜂同时探索。

### 2. Windows 下 fork 是大坑

- Windows 的进程模型和 Unix 不同，多 agent 同时生成子进程容易触发 fork 重试失败。
- **应对**：关掉不必要的程序释放内存；控制并发数；优先用 sonnet/haiku 降低单 agent 开销。
- **编码问题**：Windows 默认 GBK 编码，输出含 Unicode 字符的脚本会报 `UnicodeEncodeError`。在脚本里显式设置 UTF-8 输出（如 Python 的 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`）。

### 3. 子 agent 的 model 只认那三个值

Agent 工具的 `model` 参数只接受 `"haiku"`、`"sonnet"`、`"opus"` 三个值——**这是 Claude Code 的硬限制**。

- 主会话可以用任何已配置的模型（包括第三方模型）。
- 但子 agent 只能从这三个里选。想让子 agent 用别的模型？办不到。
- **推荐**：子 agent 默认 `sonnet`（平衡能力和成本）；轻量查找/格式化用 `haiku`；架构决策/深度分析用 `opus`。

### 4. SendMessage 别忘了 summary

给 agent 发消息时，如果是字符串消息，**必须带 summary 参数**，否则报错：

```
SendMessage(to="agent-name", summary="5-10字摘要", message="消息内容")
```

summary 是给团队协调用的简短描述，漏了就直接失败——这是多 agent 协作里最常见的低级错误。

### 5. 团队会断线，要有重建预案

- agent 的运行状态存在内存/临时目录里，session 恢复或 MCP 断开后，agent 进程会断。
- **重建流程**：先查团队配置和进程列表确认状态；如果进程全断了，清掉旧的团队/任务目录，重新下达团队创建指令。
- **Git Worktree 是更稳的隔离方式**：worktree 级隔离比进程级更耐断线，但代价是不可见（看不到 agent 在干嘛）。要可见性还是要稳定性，按场景权衡。

### 6. 在 CLAUDE.md 里声明你的 agent 偏好

不同模型对 agent 形态有偏好（有的倾向可见的进程级 agent，有的倾向不可见的 worktree agent）。如果你的工作流依赖某一种，**在项目 CLAUDE.md 里明确写死**：

```markdown
# Agent Configuration
生成子 agent 时，统一用 teammate 系统（team_name + name 参数），
不要用 isolation: "worktree"。这样 agent 可见、可监控。
```

不写死，模型可能自作主张选了你不想要的那种。

---

## 心法速查卡

1. **验证 > 信任** — 给它验证手段，别盲目信任输出。
2. **上下文是最贵的资源** — `/clear` 是好朋友，子代理是上下文防火墙。
3. **具体 > 模糊** — 一次精准指令胜过三次模糊修正。
4. **先探索再编码** — Plan Mode 是投资不是开销。
5. **配置是长期杠杆** — CLAUDE.md / Hooks / Skills 上花的时间，每次会话都在回报。
6. **预批准而非跳过权限** — 白名单 > 关掉安全门。
7. **犯错后更新规则** — 每个错误都是改进 CLAUDE.md 的机会。
8. **skill 三件套 + 渐进式披露** — SKILL.md 精简，详细内容拆子文件按需读。
9. **装 skill 先审安全** — 别让别人的脚本在你机器上裸跑。
10. **多 agent 2-3 个起步** — Windows fork、model 限制、SendMessage summary 都是坑。
