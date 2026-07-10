# 团队模板与项目注册表(reference)

> 本文件按需读取:[1/6] 读注册表 / [2/6] 组团队时加载。

## 一、团队模板(4 个)

### full-stack-team(4 人 · 前后端协作新功能)

| # | 角色 | 职责 | 模型 | subagent_type | 依赖 |
|---|---|---|---|---|---|
| 1 | architect | 接口/架构设计 | opus | Plan | 无 |
| 2 | backend | 后端实现 | sonnet | general-purpose | #1 |
| 3 | frontend | 前端页面 | sonnet | 前端专项(回退 general-purpose) | #1 |
| 4 | tester | 用例/验证 | haiku | general-purpose | #2,#3 |

### code-review-team(3-4 人 · 大规模代码审查)

| # | 角色 | 职责 | 模型 | subagent_type |
|---|---|---|---|---|
| 1 | screener | 资格初筛(过滤无关文件) | haiku | Explore |
| 2-4 | reviewer × N | 并行专项审查(安全/性能/正确性) | sonnet | code-reviewer |
| 末 | grader | 综合打置信度分(阈值 80 才发评论) | haiku | general-purpose |

### refactor-team(3-5 人 · 跨文件重构)

| # | 角色 | 职责 | 模型 | subagent_type | 依赖 |
|---|---|---|---|---|---|
| 1 | planner | 重构方案 + 影响评估 | opus | Plan | 无 |
| 2-N | refactorer × N | 分模块并行重构 | sonnet | general-purpose | #1 |
| 末 | integrator | 集成 + 回归 | sonnet | general-purpose | #2..N |

### cross-project-fullstack(4 人 · 跨仓库,凸显注册表)

| # | 角色 | 项目 | 职责 | 模型 | 依赖 |
|---|---|---|---|---|---|
| 1 | api-designer | app-backend | 接口设计 | opus | 无 |
| 2 | be-dev | app-backend | 后端实现 | sonnet | #1 |
| 3 | fe-dev | app-sibling | 前端实现 | sonnet | #1 |
| 4 | mobile-dev | app-mobile | 移动端 | sonnet | #1 |

> 项目信息由 [1/6] 注册表自动填充到各 Agent prompt(路径 / CLAUDE.md / 技术栈)。

## 二、模型速查

| 模型 | 用途 |
|---|---|
| `opus` | 架构、安全、复杂推理 |
| `sonnet` | 常规开发(默认) |
| `haiku` | 简单验证、初筛、打分 |

> 子 Agent 的 model 只支持 sonnet / opus / haiku。

## 三、subagent_type 速查

| subagent_type | 用途 |
|---|---|
| `general-purpose` | 默认,复杂多步骤 |
| `Explore` | 只读搜索分析 |
| `Plan` | 只读架构设计 |
| `code-reviewer` | 代码审查 |

> **团队自定义类型**(如前端专项 `fe-dev`、小程序专项)需团队预置到 `.claude/agents/`。**不存在时回退 `general-purpose`**,并在 [2/6] 蓝图标注。

## 四、项目注册表

一次配置多次复用:`.claude/project-registry.json`。

### schema

```json
{
  "version": 1,
  "projects": [
    { "name": "app-backend",  "path": ".",             "role": "当前项目", "description": "后端主服务",        "type": "java"  },
    { "name": "app-sibling",  "path": "../app-sibling", "role": "关联服务", "description": "通过 XxxService 对接", "type": "java"  },
    { "name": "app-mobile",   "path": "../app-mobile",  "role": "移动端",   "description": "移动端前端",          "type": "node" }
  ]
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 项目标识 |
| `path` | 是 | 项目路径(`"."`=当前项目) |
| `role` | 否 | 项目角色,辅助任务分配 |
| `description` | 否 | 注入 Agent 上下文 |
| `type` | 否 | java/node/python/mixed,影响 subagent_type 选择 |

### [1/6] 工作逻辑

```
1. 读取注册表 → 路径可达性验证(test -d / ls -d)
2. 增量同步:扫描 ../*/ 发现未注册的 git 仓库 → 自动追加
3. 任务分析时匹配涉及项目 → 模糊时询问用户
4. Agent prompt 自动填充项目信息(路径、CLAUDE.md、技术栈)
```

### 首次自动初始化

| 缺失文件 | 自动动作 |
|---|---|
| `.claude/CLAUDE.md` | 扫描项目结构 → 生成标准 CLAUDE.md → ⚠️ 展示确认 |
| `.claude/project-registry.json` | 全量扫描兄弟 git 项目 → 自动注册 → ⚠️ 展示确认 |

```
> ### ⚠️ 需要确认:项目初始化
> CLAUDE.md / 注册表 已自动生成,请审阅上方内容。
> 👉 请回复:`确认` 保存 | `修改` 补充信息 | `跳过` 不生成
```

**增量同步**:后续每次运行,自动检测兄弟目录是否有新项目 → 自动追加。可随时编辑注册表补充 `role` / `description`。

### 路径验证与降级
- 注册表路径不可达 → 跳过该项目并警告,不影响其他项目。
- 全部路径不可达 → 回退单项目模式 + 警告。

---

*本文件由 SKILL.md 按需加载,不预读。*
