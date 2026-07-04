# Claude Code Skills 集合（团队 Skill 仓库 demo）

一组适配 **Claude Code** 的通用化 skill + 团队规范。读者可整个复制到自己项目的 `.claude/` 下使用，也可作为「怎么写 Claude Code skill / 怎么资产化团队规范」的参考。

对应教程：[阶段 3 基础设施·Skill 仓库](../../pages/stage3.html) / [阶段 4 闭环试点](../../pages/stage4.html) / [阶段 6 沉淀复用](../../pages/stage6.html)。

## 这是什么

Claude Code 的 skill 是「可复用的工作流 + 领域知识」，AI 按需调用；rule 是「始终生效的规范」，AI 自动遵守。本目录是一组 skill + rule 的集合（团队 Skill 仓库 demo），用统一的 `.claude/` 布局组织。

## Skill 清单（4 个）

| Skill | 类型 | 用途 |
|---|---|---|
| [devflow](./skills/devflow/) | 编排型 | 开发工作流：需求→交付 6 阶段（编排 OpenSpec + Superpowers），断点续传 + 规则覆盖 |
| [sql-query](./skills/sql-query/) | 工具型 | PostgreSQL 只读查询（三模式 + 安全护栏：仅 SELECT/SSH 隧道/租户隔离）+ 模板/schema 双策略 |
| [crud-gen](./skills/crud-gen/) | 工具型 | CRUD 代码脚手架生成（读表结构 → 分层 domain/dto/service/dao/controller + 字段→操作符映射） |
| [code-review](./skills/code-review/) | 编排型 | AI 代码审查（红/黄/绿三级分级 + 依据下方 rule 规范自动核对 + 结构化报告） |

## 团队规范集合（`rules/`，12 份通用 rule，复制到 `.claude/rules/` 即用）

按职能分层，配合 [team-conventions.md](./rules/team-conventions.md)（通用 CLAUDE.md 总纲，用 `@` 引用下面所有 rule）：

- **入口**：[team-conventions](./rules/team-conventions.md)（CLAUDE.md 总纲：技术栈/结构/核心原则/规范索引）
- **分层与接口**：[api-response](./rules/api-response.md)（统一响应模型）· [service-dao](./rules/service-dao.md)（接口/实现分离 + 事务归 Service）
- **质量与稳定**：[error-handling](./rules/error-handling.md)（业务异常/空 catch/空值）· [logging](./rules/logging.md)（日志级别/格式/脱敏）· [testing](./rules/testing.md)（Given-When-Then/命名/禁止行为）
- **数据**：[database](./rules/database.md)（表/字段/索引/向后兼容）· [batch](./rules/batch.md)（批量代替循环）
- **并发**：[async](./rules/async.md)（线程池/上下文传递）· [distributed-lock](./rules/distributed-lock.md)（Redisson/锁粒度）
- **工程规范**：[git-branch](./rules/git-branch.md)（分支命名/Conventional Commits）· [naming](./rules/naming.md)（类后缀/方法动词/目录分层）

> 另有 [devflow.md](./rules/devflow.md) 是 devflow skill 的「覆盖规则」（改写底层 skill 默认出口），不属于团队规范。

## 实战心法

[best-practices.md](./best-practices.md) — Claude Code 用得顺手的 **8 条心法**（验证驱动/Plan Mode/上下文管理/子代理防火墙/五件套辨析/Headless/多会话并行）+ skill 写得值钱的 **5 条方法论**（SKILL.md 三件套/渐进披露/编排不实现/命名空间/安全审核）+ 多 Agent 避坑 **6 条** + 速查卡。

> README 讲「仓库怎么用」，best-practices 讲「怎么用得顺手」。

## 目录结构（`.claude/` 布局）

```
claude-skills/
├── skills/              # 各 skill 自包含一个目录
│   ├── devflow/         # SKILL.md + guide + stages/（编排型）
│   ├── sql-query/       # SKILL.md + queries.json + scripts/（工具型·查询）
│   ├── crud-gen/        # SKILL.md（工具型·代码生成）
│   └── code-review/     # SKILL.md（编排型·审查）
├── rules/               # 规则文件（team-conventions 总纲 + 11 分层规范 + devflow 覆盖规则）
├── best-practices.md    # 实战心法
└── settings.json        # 配置样例（hooks / 权限）
```

**三件套**：一个 skill = `SKILL.md`（入口）+ 可选 `reference/scripts`（按需加载）+ 可选 `rules/<name>.md`（覆盖规则）。

## 怎么装到你的项目

把需要的 skill + rule 复制到自己项目的 `.claude/` 下：

```bash
# 例：装 devflow + 团队规范到你的项目
cp -r skills/devflow       /your-project/.claude/skills/
cp rules/devflow.md        /your-project/.claude/rules/

# 装团队规范（CLAUDE.md 用 @ 引用 rule，AI 自动加载）
cp rules/team-conventions.md  /your-project/.claude/rules/
cp rules/{testing,error-handling,database,...}.md  /your-project/.claude/rules/
# 然后在项目根 CLAUDE.md 里 @ 引用它们
```

> **加载机制**：`SKILL.md` 的 frontmatter（name + description）常驻上下文，正文按需读取；rule 被 CLAUDE.md `@` 引用后始终生效——所以 frontmatter description 要写清「何时触发」，rule 要写清「AI 必须守的规范」。

## 怎么加新 skill / rule（统一管理约定）

1. skill 放 `skills/<name>/`，写 `SKILL.md`（frontmatter + 正文）；复杂内容拆 `reference/scripts` 按需加载
2. 规范放 `rules/<name>.md`，在 `team-conventions.md` 用 `@` 引用
3. 如需覆盖底层 skill 行为，在 `rules/<name>.md` 写覆盖规则（如 devflow.md）
4. 在上方「Skill 清单 / 团队规范集合」加一行

**写好 skill 的 4 个关键**（devflow 的实践总结）：
- **编排不实现**：能调底层 skill / 框架就调，不重造轮子
- **渐进式披露**：SKILL.md 精简，详细内容拆到子文件按需读
- **恢复判定**：长流程要有「中断后从哪继续」的逻辑
- **覆盖规则**：`rules/` 始终生效，用来改写底层 skill 的默认出口 / 边界

## 可单独交付

本目录自包含，可独立打包分发。结合教程的 [角色操作手册](../role-handbooks/) 和 [汇报材料](../report-templates/)，构成「团队 AI 转型」的完整资产包。
