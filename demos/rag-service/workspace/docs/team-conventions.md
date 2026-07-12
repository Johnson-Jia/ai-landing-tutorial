# 团队代码规范

## 总则

本规范适用于全组后端与前端工程,目的是保证代码可读、可维护、可协作。任何人提交代码都必须遵守以下规则,违反者 Code Review 不予通过。

## 分支策略

我们采用 trunkbased 主干开发 + 短期 feature 分支的混合模式:

- `master`:始终可发布,所有提交必须经过 Code Review 与 CI 通过。
- `feat/<jira-id>-<short-desc>`:功能分支,生命周期不超过 3 天。
- `fix/<jira-id>-<short-desc>`:修复分支。
- `hotfix/<short-desc>`:线上紧急修复,从 master 切出,合回 master 后同步到下个 release。

禁止直接 push 到 master,所有变更走 PR/MR。

## Commit Message 规范

使用 Conventional Commits:

- `feat(scope): 新功能`
- `fix(scope): 修复`
- `refactor(scope): 重构`
- `docs(scope): 文档`
- `test(scope): 测试`
- `chore(scope): 杂项`

scope 是模块名(如 `auth`、`rag`、`ui`)。message 全部用中英文均可,但必须能体现意图。禁止 "update"、"fix bug" 这类无信息量的 message。

## 命名约定

- 变量/函数:`camelCase`(JS/TS)或 `snake_case`(Python)。
- 类:`PascalCase`。
- 常量:`UPPER_SNAKE_CASE`。
- 文件:小写连字符 `kebab-case.ts`。
- 数据库表/字段:`snake_case`,表名复数。
- 布尔变量以 `is/has/can` 开头,如 `isEnabled`、`hasPermission`。

## Code Review 流程

1. 提交 PR,填写模板(改了什么、为什么、如何测试)。
2. 至少 1 名 reviewer 审核通过(owner 可指定 2 名)。
3. CI 全绿(单测、lint、构建)。
4. reviewer 关注:正确性、可读性、性能、安全、是否符合规范。
5. 合并采用 squash merge,保留清晰 message。
6. 合并后作者负责删除 feature 分支。
