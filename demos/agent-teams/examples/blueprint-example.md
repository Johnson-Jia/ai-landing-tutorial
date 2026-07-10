# 团队蓝图示例:标准并行(独立模式)

> 场景:开发用户认证功能(注册 + 登录 + JWT 接口),单项目。展示 6 步完整流程的标准并行走法。

## [1/6] 环境检测

```
[1/6] 环境检测
  初始化: ✅
  模式: 独立
  范围: 单项目
  Swarm: ❌ 未启用(将回退标准并行)
```

## [2/6] 团队蓝图(full-stack-team)

```
任务目标: 用户认证系统(注册 + 登录 + JWT)

| # | 角色      | 职责       | 模型   | subagent_type                | 依赖  | 验收标准                          |
| 1 | architect | 接口设计   | opus   | Plan                         | 无    | 产出接口文档,覆盖注册/登录/JWT 用例 |
| 2 | backend   | JWT 接口   | sonnet | general-purpose              | #1    | 实现注册/登录/JWT,单测通过         |
| 3 | frontend  | 登录注册页 | sonnet | 前端专项(回退 general-purpose) | #1    | 页面联通接口,注册→登录 可演示      |
| 4 | tester    | 用例验证   | haiku  | general-purpose              | #2,#3 | 单测覆盖注册/登录/JWT 核心用例     |
```

## [3/6] 🔴 必须确认

```
> ### 🔴 必须确认:即将执行
> 以上为完整团队计划,确认后将立即启动 Agent 执行。
> 👉 请回复:`确认` 开始执行 | `修改` 调整蓝图
```

## [4/6] 并行执行

```
🚀 architect 启动中...(Plan / opus)
🚀 backend   启动中...(general-purpose / sonnet)
🚀 frontend  启动中...(general-purpose / sonnet)
🚀 tester    等待 #2,#3 完成...(general-purpose / haiku)

执行进度:
  #1 architect  ✅ 完成 (接口文档,2个文件)
  #2 backend    ⏳ 运行中...
  #3 frontend   ⏳ 运行中...
  #4 tester     🚀 等待 #2,#3 结果...

执行进度:
  #1 architect  ✅ 完成 (接口文档,2个文件)
  #2 backend    ✅ 完成 (JWT 接口,5个文件)
  #3 frontend   ✅ 完成 (登录注册页,3个文件)
  #4 tester     ✅ 完成 (单测用例,4个文件)
```

## [5/6] 质量验收

```
[5/6] 质量验收
  ✅ architect: 接口文档覆盖全部用例
  ✅ backend:   注册/登录/JWT 实现,单测通过
  ✅ frontend:  页面联通接口,注册→登录 可演示
  ✅ tester:    单测覆盖注册/登录/JWT 核心用例
```

## [6/6] 结果交付

```
[6/6] 执行报告
  成功: 4/4 | 失败: 0/4
  ✅ architect: 接口文档(2个文件)
  ✅ backend:   JWT 接口(5个文件)
  ✅ frontend:  登录注册页(3个文件)
  ✅ tester:    单测用例(4个文件)
  汇总: 用户认证系统已实现,前后端联通,核心用例有单测覆盖
  建议: 补充刷新 token、第三方登录
```

---

## 附:Agent 失败处理示例([4/6])

```
执行进度:
  #1 architect ✅ 完成 (接口文档,2个文件)
  #2 backend   ❌ 失败: 缺少用户表 DDL,DAO 层无法生成
  #3 frontend  ⏳ 运行中...
  #4 tester    🚀 等待 #2,#3 结果...

> ### ⚠️ Agent 执行失败
> backend 执行失败:缺少用户表 DDL,DAO 层无法生成
> 👉 请选择:`重试` | `跳过` 该任务 | `终止` 全部

用户: 重试,补充表结构 t_user(user_id, username, password_hash, created_at, ...)

🚀 backend 重试中...(general-purpose / sonnet)

执行进度:
  #1 architect ✅ 完成 (接口文档,2个文件)
  #2 backend   ✅ 完成 (用户 DAO + JWT,6个文件)
  #3 frontend  ✅ 完成 (登录注册页,3个文件)
  #4 tester    ✅ 完成 (单测用例,4个文件)
```
