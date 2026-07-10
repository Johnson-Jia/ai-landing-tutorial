# Agent Teams · 多 Agent 并行编排 Skill(demo)

一个 Claude Code **编排型** skill:一条命令拉起多 Agent 团队,把跨文件重构 / 大规模审查 / 多角色协作等复杂任务,拆成 6 步自动跑完。编排 Claude Code 原生 Agent 工具,**自己不实现业务逻辑**。

对应教程:[阶段 5 推广度量 · 多 Agent 并行](../../pages/stage5.html)。

## 这是什么

agent-teams 是「多 Agent 编排器」:你说一句"拉个团队做 XX",它走 6 步——**环境检测 → 分析蓝图 → 🔴确认 → 并行执行 → 质量验收 → 结果交付**——把任务派给一组子 Agent 并行干完,验收合格才交付。

它自己不写业务逻辑,只做三件事:**组队**(按团队模板拆角色)、**调度**(按依赖拓扑并行派 Agent)、**把关**(5 个确认点 + 质量验收打回闭环)。

> 这是**编排型 skill**——学它的价值在 4 个设计手法:①编排不实现 ②人在回路确认闸门 ③项目注册表跨项目复用 ④优雅降级。

## 前置依赖

| 依赖 | 必需? | 说明 |
|---|---|---|
| Claude Code(Agent 工具) | ✅ 必需 | 提供 subagent 调度、Skill 加载 |
| Swarm 协作 | ⚪ 可选 | 设环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`;不设自动回退标准并行 |
| devflow skill | ⚪ 可选 | 装了可联动 devflow 的 Stage 4;不装走独立模式 |
| bash + python3 | ✅ 自检 | 仅 `verify.sh` 用,标准库即可 |

> **诚实声明**:核心 6 步流程在标准 Claude Code 可跑;Swarm / devflow 集成为**可选增强**,取决于你的环境——不承诺所有功能在所有环境全跑通。每个可选依赖都有自动回退(见 `SKILL.md`「降级规则」)。

## 怎么装

把整个目录复制到自己项目的 `.claude/skills/agent-teams/`。

**Mac / Linux**:
```bash
cp -r demos/agent-teams  /your-project/.claude/skills/agent-teams
```

**Windows**(或直接用资源管理器拖文件夹):
```powershell
xcopy /E /I demos\agent-teams  your-project\.claude\skills\agent-teams
```

可选:把 `settings.json` 的 `permissions` / `env` 合并进你项目的 `.claude/settings.json`(启用 Swarm 记得把 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 改 `1`)。

## 怎么用

装好在项目根启动 Claude Code,然后:

```
/agent-teams 开发用户认证功能,含注册登录页和后端 JWT 接口
```

或自然语言(命中关键词即可):「帮我拉个团队做 XX」「多 agent 并行重构 XX」「跨项目加个 XX 功能」。

完整对话样例见 [`examples/blueprint-example.md`](./examples/blueprint-example.md),通读手册见 [`manual.md`](./manual.md)。

## 装完怎么验证

### L1 · 自检(本地必跑)

```bash
bash demos/agent-teams/scripts/verify.sh
```

检查:frontmatter 合法 / 必需文件齐全 / 注册表 JSON 可解析。退出码 `0` = 包完整、可被 Claude Code 加载;`1` = 有缺失,会打印缺什么。

### L2 · 端到端(真实 Claude Code 手动)

1. 复制到 `.claude/skills/agent-teams/` → 启动 Claude Code
2. 说「拉个团队做 XX」→ 命中触发词
3. 6 步走通:环境块 → 蓝图 → 🔴确认 → 派 Agent → 验收 → 报告
4. 降级验证:不设 Swarm env var → 自动回退标准并行(不报错)

## 目录结构

```
agent-teams/
├── SKILL.md                     # Skill 入口(AI 读):frontmatter + 6 步 + 策略 + 降级
├── manual.md                    # 人话操作手册(你读)
├── settings.json                # 配置样例(权限 / Swarm 开关)
├── reference/                   # 按需加载(AI 细节)
│   ├── orchestration.md         #   4 策略 + Swarm + devflow 集成
│   └── team-and-registry.md     #   团队模板 + 模型速查 + 注册表
├── examples/
│   ├── project-registry.json    #   注册表示例
│   └── blueprint-example.md     #   标准并行完整样例
└── scripts/
    └── verify.sh                #   自检
```

**三件套**:`SKILL.md`(入口)+ `reference/`(按需细节)+ `examples/`(样例)。这是 Claude Code skill 的标准组织:frontmatter 常驻上下文、正文按需读取、细节渐进披露。

## 与 claude-skills 的关系

- [`demos/claude-skills/`](../claude-skills/) 是**单 skill 仓库**(devflow / sql-query / crud-gen / code-review),agent-teams 是**多 Agent 编排层**,体量与定位不同,所以独立成包。
- agent-teams 的「devflow 集成」可选模式,联动对象就是 claude-skills 里的 devflow skill。
- 写法同轮:都遵循「编排不实现 / 渐进披露 / 覆盖规则」的 skill 心法(见 claude-skills 的 [`best-practices.md`](../claude-skills/best-practices.md))。

## 可单独交付

本目录自包含,可独立打包分发。配合教程的 [角色手册](../role-handbooks/) 和 [汇报材料](../report-templates/),构成「团队 AI 转型」的完整资产包。
