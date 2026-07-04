---
name: sql-query
description: "PostgreSQL 只读查询助手（工具型 skill）。三模式：查连接信息 / 同步表结构 / 执行 SQL。安全护栏：仅 SELECT、SSH 隧道、租户隔离自动加 corp_code。模板匹配优先，schema 构造兜底。"
license: MIT
compatibility: 需 psycopg2 + SSH 隧道访问
metadata:
  author: "Johnson"
  version: "1.0"
---

# SQL 查询技能（工具型 skill · 含安全护栏）

PostgreSQL 数据库只读查询助手。支持三种模式：连接信息查询、表结构同步、SQL 查询。

> 这个 skill 是「工具型 skill + 安全护栏」的范例——和编排型（devflow）不同，工具型 skill 自己实现功能（连库查数据），所以**安全护栏是命门**：仅 SELECT、SSH 隧道、租户隔离（自动加 corp_code），缺一条都可能酿成事故。

## 模式一：查询数据库连接信息

当用户说「查数据库连接」「数据库地址」「JDBC」等，用 `--info` 模式：

```bash
python3 ~/.claude/skills/sql-query/scripts/pg_tunnel_query.py --info <corp_code>
```

返回连接信息（租户、环境、JDBC URL、主机、端口、库名、用户），表格展示。

## 模式二：同步数据库表结构

当用户说「同步表结构」「拉取 schema」「查表结构」，用 `--schema` 模式：

```bash
python3 ~/.claude/skills/sql-query/scripts/pg_tunnel_query.py --schema <corp_code>
```

执行后在 `schemas/` 生成 `{env}_schema.json`（同环境共享一份，只需同步一次），含所有用户表结构 + 表间关联。

## 模式三：执行 SQL 查询

### 前置：读本地 schema

查询前**必须先读** `schemas/{env}_schema.json`：获取表名、字段、注释、表间关联（relationships）。文件不存在或超 7 天未更新，建议先 `--schema` 同步。

### 第一步：模板匹配（优先）

读 `queries.json`，看用户中文需求是否命中模板：
1. 用关键词匹配 `triggers` 数组
2. 命中 → 提取参数填充 `sql` 的 `{参数名}` → 直接执行
3. 未命中 → 走第二步（schema 构造）

**加新模板**：常用 SQL 追加到 `queries.json`（name/module/triggers/sql/params/param_hint）。

### 第二步：schema 构造（兜底）

未命中模板时（如「查某用户的培训记录」）：
1. 用 `tables.comment` 匹配相关表
2. 用 `relationships` 定位 JOIN 条件
3. 用 `columns.comment` 选列
4. 构造含正确表名/列名/JOIN 的 SQL

### 执行

```bash
python3 ~/.claude/skills/sql-query/scripts/pg_tunnel_query.py <corp_code> "<sql>"
```

结果表格返回。

## 安全护栏（命门）

- **仅 SELECT**：脚本硬性拒绝写操作（INSERT/UPDATE/DELETE/DROP）
- **SSH 隧道**：每次查询自动建/关隧道，不在脚本里留长连接
- **租户隔离**：执行 SQL 自动加 `corp_code` 条件，防止跨租户查数据
- **自动 LIMIT**：无 LIMIT 自动加 `LIMIT 2000`，防全表扫描
- **SQL 不加分号**

> 这五条护栏是这个 skill 能进生产的根本。工具型 skill 接触真实数据，**护栏比功能更重要**——见教程阶段 1 §6.1 数据边界、阶段 6 §3.1 三条红线。
