# Git 分支与提交规范（通用 rule 模板）

> Git 分支与提交规范：分支命名 + Conventional Commits + 提交前检查。放 `.claude/rules/git-branch.md`。

## 分支命名格式

### 功能 / Bug 修复（带任务号）

```
{username}/{type}/{ticket}/{description}
```

### 其他类型

```
{username}/{type}/{description}
```

- `username`：取 `git config user.name`
- `ticket`：你的任务跟踪系统编号（Jira / Issue / 工单号），如 `PROJ-1234`
- `description`：小写、空格转 `-`，简短描述
- 时间戳可选（团队约定要时再加：`{yyyyMMddHHmmss}`）

## 示例

```
alice/feat/PROJ-7042/login-api
alice/fix/PROJ-19611/payment-error
alice/docs/api-readme
alice/refactor/user-module
```

## 允许的 type

| type | 适用场景 |
|------|----------|
| feat | 新功能 |
| fix | Bug 修复 |
| refactor | 重构（不改功能） |
| hotfix | 线上紧急修复 |
| chore | 构建 / 依赖 / 配置 |
| docs | 文档 |
| style | 格式调整 |
| perf | 性能优化 |
| test | 测试 |

## 创建分支必做步骤

AI 创建分支时必须：

1. 读取 `git config user.name` 作为 username
2. 切换到主干分支（`master` / `main`）
3. `git pull` 拉最新
4. 任务号（如有）校验格式
5. description 转小写 + 空格转 `-`
6. `git checkout -b {新分支名}`

## 提交信息格式（Conventional Commits）

```
<type>(<scope>): <subject>

[可选 body：说明 why，不写 what]

[可选 footer：Closes PROJ-1234]
```

### Type 允许值

```
feat      新功能
fix       Bug 修复
docs      文档
refactor  重构
style     格式
test      测试
chore     构建 / 工具
perf      性能
```

### 规则

- subject ≤ 72 字符
- 用动词开头（add / fix / update / remove / optimize）
- ❌ 不允许：`update code` / `fix bug` / `修改代码` / `修复问题`（无信息量）

### 示例

```
feat(user): 新增学习计划自动分配功能

根据用户所在部门自动匹配并分配对应计划。

Closes PROJ-1234
```

## 提交前必做检查

1. 编译通过（`mvn clean compile` / `npm run build` / 对应命令）
2. 无 `System.out.println` 或 `e.printStackTrace()`
3. 无注释掉的废弃代码块
4. 无硬编码的 IP / 密码 / 密钥 / token
5. 对外接口（API 模块）签名变更，确认不破坏已有调用方
6. 测试与代码一起提交

## 禁止行为

- ❌ 直推 `master` / `main` / `develop`
- ❌ 提交 `.env`、凭据、密钥文件
- ❌ 一个提交塞多个不相关改动（拆成多个提交）
- ❌ `--no-verify` 绕过 hooks

---
> 相关：`naming.md`（命名）、`team-conventions.md`（核心原则）。
