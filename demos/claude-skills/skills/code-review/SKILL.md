---
name: code-review
description: "代码审查（编排型 skill）。按分层规范审查当前改动，输出分级问题清单 + 修复建议。覆盖 Controller/Service/DAO/日志/异常/通用项，红灯必改黄灯建议改。引用 rules/ 下的规范文件作为依据。"
license: MIT
metadata:
  author: "Johnson"
  version: "1.0"
---

# 代码审查技能（编排型 skill · 按规范审查改动）

对当前改动（`git diff`）按分层规范做代码审查，输出分级问题清单和修复建议。

> 这是「编排型 skill」的范例——和工具型（sql-query 连库查数据）不同，编排型 skill 不自己实现功能，而是**编排「读 diff → 按规范逐项检查 → 输出结构化报告 → 询问是否修复」**这个流程。价值在**把团队的审查 checklist 固化成 AI 可执行的步骤**，规范依据来自 `rules/` 下的 rule 文件。

## 输入

- 审查范围（可选）：当前文件 / 当前分支所有改动 / 指定文件路径。默认当前改动。

## 执行步骤

### 1. 获取改动

```bash
git status
git diff          # 已暂存 + 未暂存
git diff --cached # 仅已暂存
```

### 2. 按分层逐项检查

> 下方「规范依据」对应 `.claude/rules/` 下的文件。严重程度：🔴 高（必改）/ 🟡 中（建议改）/ 🟢 低（提示）。

#### Controller 层

| 检查项 | 规范依据 | 严重 |
|---|---|---|
| 返回值是否用统一响应模型包装 | api-response.md | 🔴 |
| 是否只做参数校验 + 调 Service | service-dao.md | 🔴 |
| 是否含业务逻辑 | service-dao.md | 🔴 |
| 是否直接调 DAO | service-dao.md | 🔴 |
| 是否在 Controller 加 @Transactional | service-dao.md | 🔴 |
| 方法是否过长（> 30 行） | — | 🟡 |
| URL / 路由命名是否符合规范 | naming.md | 🟡 |

#### Service 层

| 检查项 | 规范依据 | 严重 |
|---|---|---|
| 接口与实现是否分离（接口在 API 模块） | naming.md | 🔴 |
| @Transactional 是否 rollbackFor = Exception.class | service-dao.md | 🔴 |
| 事务方法是否为 public、未被同类自调用 | service-dao.md | 🔴 |
| 事务内是否调外部 HTTP / RPC / 发 MQ | service-dao.md | 🔴 |
| Service 实现里是否写 SQL（应归 DAO） | service-dao.md | 🟡 |

#### DAO 层

| 检查项 | 规范依据 | 严重 |
|---|---|---|
| 是否用 `SELECT *`（应明确列字段） | service-dao.md | 🔴 |
| 是否循环内执行 SQL（N+1） | batch.md | 🔴 |
| IN 子句是否用命名参数 | batch.md | 🟡 |
| IN 子句是否超 500 未分批 | batch.md | 🟡 |
| 是否含业务逻辑判断（应归 Service） | service-dao.md | 🔴 |

#### 日志

| 检查项 | 规范依据 | 严重 |
|---|---|---|
| 是否用 `System.out.println` | logging.md | 🔴 |
| 是否用 `e.printStackTrace()` | logging.md | 🔴 |
| 是否打印敏感信息（密码 / token / 身份证） | logging.md | 🔴 |
| 是否用字符串拼接而非占位符 | logging.md | 🟡 |
| 日志前缀是否规范（`[ClassName]`） | logging.md | 🟢 |

#### 异常处理

| 检查项 | 规范依据 | 严重 |
|---|---|---|
| 是否空 catch 块 | error-handling.md | 🔴 |
| catch 后是否只打日志不处理（不返回 / 不重抛） | error-handling.md | 🔴 |
| 是否直接抛 `RuntimeException`（应业务异常） | error-handling.md | 🟡 |
| Controller 是否对异常做了合理响应 | api-response.md | 🟡 |

#### 批量操作（改动涉及循环 / 集合时）

| 检查项 | 规范依据 | 严重 |
|---|---|---|
| 循环内是否单条查询 / 更新 | batch.md | 🔴 |
| 循环内是否调 Service（应直接 DAO） | batch.md | 🔴 |
| 大批量是否分批（每 500） | batch.md | 🟡 |

#### 通用

| 检查项 | 严重 |
|---|---|
| 未使用的 import | 🟢 |
| 注释掉的废弃代码 | 🟡 |
| 硬编码 IP / 密码 / 密钥 | 🔴 |
| TODO / FIXME 未处理 | 🟢 |

### 3. 输出格式

```markdown
## 代码审查报告

### 概览
- 检查文件数：X 个
- 问题总数：Y 个
  - 🔴 高危：A
  - 🟡 中等：B
  - 🟢 建议：C

### 🔴 高危问题（必须修复）
| 文件 | 行号 | 问题描述 | 规范依据 | 修复建议 |
|------|------|----------|----------|----------|
| XxxController.java | 45 | Controller 含业务逻辑 | service-dao.md | 将逻辑移至 Service |

### 🟡 中等问题（建议修复）
| 文件 | 行号 | 问题描述 | 规范依据 | 修复建议 |
|------|------|----------|----------|----------|
| XxxServiceImpl.java | 78 | 日志未用占位符 | logging.md | 改为 log.info("x={}", v) |

### 🟢 改进建议
| 文件 | 建议 |
|------|------|
| XxxDAO.java | 建议补批量查询方法 |

### 通过项
- 响应包装：通过
- 事务使用：通过
- ...
```

### 4. 交互确认

报告输出后询问：

1. 是否自动修复可修复的问题？
2. 是否查看某个问题的详细说明？

## 设计要点

- **依据可追溯**：每条问题挂「规范依据」，指向 `rules/` 具体文件——AI 不是凭感觉挑刺，是按团队成文规范审。
- **分级**：红灯必改（架构 / 安全 / 性能），黄灯建议，绿灯提示。避免把所有问题堆成一锅。
- **编排型不自己写规则**：检查项的「标准」由 rule 文件定义，skill 只负责「跑流程」。团队加新规范时改 rule，不改 skill。
- **可裁剪**：没有对应 rule 文件的项目，删掉对应检查项即可；新增分层（如前端组件）按同表格扩展。

---
> 相关：`rules/` 下各分层 rule 文件（api-response / service-dao / batch / naming / git-branch / logging / error-handling）。
