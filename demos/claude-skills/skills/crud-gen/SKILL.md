---
name: crud-gen
description: "CRUD 代码脚手架（工具型 skill）。读数据库表结构，一键生成分层 CRUD 代码（domain/dto/service/dao/controller）。通用分层范式，DAO 层按你的 ORM 适配。"
license: MIT
metadata:
  author: "Johnson"
  version: "1.0"
---

# CRUD 代码生成器（工具型 skill · 脚手架生成）

读数据库表结构，一键生成标准分层的 CRUD 代码——把重复的脚手架劳动交给 AI。

> 这是「工具型 skill · 代码生成」的范例。和 sql-query（查询数据）不同，crud-gen 是「生成代码」。价值在**分层范式 + 字段→操作符映射**，不绑定特定 ORM（DAO 层按你的 MyBatis / JPA / JDBC 适配）。

## 分层结构（生成内容）

按表生成标准分层，生成代码统一放 `modules/` 包（与手写业务代码分离）：
```
modules/{entity}/
├── domain/        # 实体 + 查询条件(Condition) + VO
├── dto/           # Create / Update DTO
├── service/       # Service 接口 + 实现
├── dao/           # DAO + ConditionBuilder（按你的 ORM）
└── controller/    # Controller + Model
```

## 字段类型 → 查询操作符映射（核心范式）

根据表的字段类型，自动生成对应的查询条件：
| 字段类型 | 生成的操作符 |
|---|---|
| String | 精确 / 模糊(Like) / In / NotIn |
| Integer / Long | 等于 / 大于 / 小于 / 范围 |
| BigDecimal | 等于 / 大于 / 小于 / 范围 |
| Date | 等于 / 开始 / 结束（日期范围）|
| Boolean | 等于 |

特殊处理：`remark` 类只生成 Like；`*Id` 字段不生成 Like / In。

## Service 标准方法
`load(id)` / `save` / `remove` / `update` / `queryList` / `pageQuery`

## Controller 标准端点
init / list / page / detail / save / remove / update（按你的路由风格调整）

## 扩展点（生成后手写业务）
- **Condition 扩展区**：加自定义查询字段
- **ConditionBuilder 扩展**：重写 `buildCustomCondition` 加自定义 SQL 条件
- **Converter 扩展**：重写 Query → Condition 转换

## 配置（crud-generator.yaml，按你的栈填）
- `database`：连接信息（**必须加进 .gitignore，别提交密码**）
- `code`：基础包路径 / 模块名 / 表前缀（生成时去除）/ 作者

## 安全护栏
- 已存在的文件**跳过不覆盖**（保护手写改动）
- 配置文件含密码，**必须 .gitignore**
- 生成的是脚手架，业务逻辑仍需人工调整 + Review（见 team-conventions 的 Code Review 四问）

---
> 工具型 skill 接触数据库配置，护栏比功能重要——参考 sql-query 的安全护栏（仅 SELECT / 配置脱敏）。
