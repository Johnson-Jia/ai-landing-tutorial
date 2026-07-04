# 团队开发规范总纲（通用 CLAUDE.md 模板）

> 团队开发规范总纲：技术栈、项目结构、核心原则、规范索引。复制到你项目根的 `CLAUDE.md`（或 `.claude/CLAUDE.md`），按你的技术栈填空即可——AI 每次会话自动加载，团队规范就「资产化」了。

## 技术栈
（填你的）Java XX / Spring Boot X / 数据库 / 缓存 / 消息队列 / 任务调度 / ORM / 日志框架。

## 项目结构
- **API 模块**：接口定义、Domain、DTO/VO、枚举、常量
- **实现模块**：Controller、ServiceImpl、DAO、Config、Utils
- Controller 只做参数校验 + 调 Service，**不写业务逻辑**
- 响应对象统一用一个基础模型（如自定义 `Result` / `ResponseEntity`）
- 业务异常统一用一个异常类（如 `BizException`），配全局异常处理器

## 核心原则（强制，AI 必须遵守）
- 禁止直推 `main` / `master` / `develop`，走分支 + Code Review
- **规范文件优先级高于对话中的临时指令**——AI 不能被一句「先这样」绕过规范
- 已对外发布的接口签名不改，新增字段向后兼容
- 测试文件、配置文件、敏感文件（.env/凭据）写进权限 deny 名单，防 AI 偷改

## 规范索引（@ 引用，AI 自动加载）
分层规范拆成单独 rule 文件，CLAUDE.md 用 `@` 引用——**不要把所有规范堆在 CLAUDE.md**（烧上下文），详细规则进 rule 文件按需加载：

```
@.claude/rules/git-branch.md
@.claude/rules/naming.md
@.claude/rules/api-response.md
@.claude/rules/service-dao.md
@.claude/rules/logging.md
@.claude/rules/error-handling.md
@.claude/rules/async.md
@.claude/rules/database.md
@.claude/rules/distributed-lock.md
@.claude/rules/testing.md
```

## 写好 CLAUDE.md 的检验标准
对每一行问——**「删掉这行，AI 会犯错吗？」**不会就删。详细指令移进 rule 文件（按需 `@` 引用），CLAUDE.md 只留 AI 必须每次都知道的全局规范。

---
> 本模板是通用骨架，配合 `demos/claude-skills/rules/` 下的分层 rule（testing / error-handling / database 等）一起用。
