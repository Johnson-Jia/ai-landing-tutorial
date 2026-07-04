# 数据库设计规范（通用 rule 模板）

> 数据库设计规范：表设计、字段、索引、变更。以 PostgreSQL 为例，核心约束与命名规则可迁移到其他关系库。放 `.claude/rules/database.md`，AI 建表/写 SQL 时自动遵守。

## 基本原则
- 关系型库（PostgreSQL 为例），ORM 用项目统一的 DAO 封装 + JdbcTemplate/MyBatis
- 表名、列名、主键名、索引名长度不超过 **30 个字符**（兼容 Oracle）
- 所有字母小写，单词间用下划线 `_` 连接

## 【强制】表命名规范
格式：`类型名_模块名_功能名_关系名（可选）`

| 类型名 | 说明 |
|--------|------|
| `t`    | 表   |
| `p`    | 存储过程 |
| `v`    | 视图 |

```sql
-- ✅ 正确
t_user_user           -- 用户模块用户表（模块名_功能名）
t_order_order_info    -- 订单模块订单信息表
t_user_user_role_rel  -- 用户角色关联表

-- ❌ 错误
user_table          -- 缺少类型名和模块名前缀
t_user              -- 缺少模块名
pg_custom_table     -- 禁止 pg_ / sql_ / sl_ 开头
```

规则：
- 表名单词数不超过 **5 个**
- 禁止 `pg_`、`sql_`、`sl_` 开头

## 【强制】字段命名规范

### 主键
每张表主键必须以表功能名作为前缀：
```sql
-- ✅ 正确：t_user_user 表的主键
user_id varchar(32)

-- ❌ 错误：禁止直接用 id
id varchar(32)
```

### 常用字段后缀规则

| 后缀          | 类型        | 长度           | 说明                              |
|-------------|-----------|--------------|----------------------------------|
| `_name`     | varchar   | 20 或 50      | 名称，较短用 20，较长用 50             |
| `_type`     | varchar   | 10 或 20      | 枚举英文单词，注释中说明每个值含义     |
| `_state`    | varchar   | 10 或 20      | 同上                              |
| `_status`   | varchar   | 10 或 20      | 同上                              |
| `_time`     | timestamp | -            | 年月日时分秒                        |
| `_date`     | date      | -            | 年月日                            |
| `_interval` | bigint    | -            | 时间跨度，单位毫秒                   |
| `_count`    | int       | -            | 次数                              |
| `_code`     | varchar   | 20 或 50      | 程序内部使用，一般不作页面展示          |
| `_comments` | varchar   | 50           | 备注                              |
| `tenant_id` | varchar   | 50           | 租户/组织 ID，固定长度                    |
| `show_order`| float     | -            | 排序号，固定命名                    |
| `category`  | varchar   | 按需           | 分类字段使用此关键字                  |
| `path`      | varchar   | 200          | 树形结构全路径，超出需说明             |

```sql
-- ✅ 正确示例
order_name   varchar(50)       -- 订单名称
order_type   varchar(10)       -- 订单类型：NORMAL/GROUP/PREPAID/...
create_time  timestamp         -- 创建时间
retry_count  int               -- 重试次数
tenant_id    varchar(50)       -- 租户ID
show_order   float             -- 排序号

-- ❌ 错误示例
type          varchar(2)        -- 缺少表名前缀；用数字表示状态
status        int               -- 禁止用数字 0/1/2 表示状态
```

### 状态值禁止用数字
```sql
-- ❌ 错误：无意义数字
state int  -- 0=启用 1=禁用 2=冻结

-- ✅ 正确：英文单词，在注释中说明含义
state varchar(10)  -- 状态：Enable/Disable/Freeze
COMMENT ON COLUMN t_user_user.state IS '用户状态：Enable-启用 Disable-禁用 Freeze-冻结';
```

## 【强制】字段数据类型规范

### varchar 长度必须使用规范级别
```
varchar(10) / varchar(20) / varchar(50) / varchar(100) /
varchar(200) / varchar(400) / varchar(800) / varchar(1300)
varchar(32)  ← 仅用于存放 UUID
```
```sql
-- ❌ 错误：非规范长度
name varchar(12)
code varchar(67)

-- ✅ 正确
name varchar(50)
code varchar(20)
```

### 浮点类型按需选择

| 类型               | 精度说明                     | 适用场景            |
|------------------|--------------------------|-----------------|
| `float`          | 最大 6 位（超出变科学计数）       | 一般数值            |
| `double precision` | 最大 16 位（超出变科学计数）    | 高精度数值           |
| `money`          | 最多 2 位小数，自动加千分位逗号    | 货币（慎用）         |
| `numeric(p,s)`   | 自定义总长度 p 和小数位 s，超长报错    | 必须精确小数的场景     |

### 禁止使用 text 类型
```sql
-- ❌ 错误：禁止在表中存放 text 类型
content text

-- ✅ 正确：大文本存对象存储/搜索引擎，表中只存片段
content_summary varchar(800)  -- 内容摘要
```

## 【强制】必须包含的公共字段
每张表必须包含以下字段：
```sql
tenant_id         varchar(50),           -- 租户/组织 ID
create_by         varchar(32),           -- 创建人
create_time       timestamp,             -- 创建时间
last_modify_by    varchar(32),           -- 最后修改人
last_modify_time  timestamp              -- 最后修改时间
```

## 【强制】索引规范

### 索引命名
格式：`i_模块名_功能名_字段名`
```sql
-- ✅ 正确
i_user_user_user_id     -- t_user_user 表的 user_id 索引
i_order_order_order_code -- t_order_order 表的 order_code 索引
i_user_user             -- 默认表示 tenant_id 索引（tenant_id 索引可省略字段名）

-- 添加索引注释（必须）
COMMENT ON INDEX i_user_user_user_id IS '用户id索引';
```

### 索引数量限制
- 单字段索引：单表不超过 **3 个**（不含主键）
- 复合索引：字段不超过 **3 个**
- 默认使用 **B-tree** 索引，使用其他类型（R-tree、Hash）需说明原因

### 复合索引注意事项
```sql
-- 索引 index(a, b, c)
-- ✅ 可以命中：(a)、(a,b)、(a,b,c)、(a,c)
-- ❌ 不能命中：(b)、(b,c)、(c)
-- 第一个字段必须出现在 WHERE 条件中
```

### 索引字段选择原则
- 频繁出现在 `WHERE` 子句中的字段
- 用于多表关联的字段
- 具有高选择性和过滤性的字段

## 【强制】唯一约束规范
命名：将表名的 `t` 替换为 `u`

```sql
-- ✅ 正确：t_user_user 表的唯一约束
ALTER TABLE t_user_user
    ADD CONSTRAINT u_user_user UNIQUE (employee_code, user_name);

-- 注：一张表原则上只有一个唯一约束，多字段组合约束
```

## 【强制】建表必须添加注释
```sql
-- 表注释
COMMENT ON TABLE t_app_app IS '应用表';

-- 字段注释（每个字段都必须有）
COMMENT ON COLUMN t_app_app.app_id     IS '主键';
COMMENT ON COLUMN t_app_app.app_name   IS '应用名称';
COMMENT ON COLUMN t_app_app.state      IS '状态：Enable-启用 Disable-禁用';

-- 索引注释
COMMENT ON INDEX i_app_app_app_code IS '应用代码索引';
```

## 【强制】缩写规范
超长命名时按优先级使用以下缩写：

| 原词          | 缩写     |
|-------------|--------|
| message     | msg    |
| system      | sys    |
| attachment  | attach |
| history     | hist   |
| channel     | chan   |
| statistics  | stats  |
| application | app    |

## 【强制】分区规范
单表数据量超过 **300W** 行时需考虑表分区，以下场景优先使用分区：
- 日志表
- 报表相关大表
- 具有清晰年度/月度边界的大表

## 【强制】向后兼容规范
```sql
-- ✅ 允许：新增字段
ALTER TABLE t_order_order_info ADD COLUMN extra_field varchar(50);

-- ✅ 允许：扩大字段长度
ALTER TABLE t_order_order_info ALTER COLUMN order_name TYPE varchar(100);

-- ❌ 禁止：删除字段
ALTER TABLE t_order_order_info DROP COLUMN order_name;

-- ❌ 禁止：修改字段类型
ALTER TABLE t_order_order_info ALTER COLUMN show_order TYPE int;
```

新增字段规则：
- 允许为空的新字段：必须在注释中说明空值含义，程序中做空值处理
- 非空的新字段：必须在数据库 Schema 层设置默认值

## 【强制】SQL 编写规范
```sql
-- ✅ 优先使用 JOIN 替代子查询
SELECT u.user_id, u.user_name, r.role_name
FROM t_user_user u
JOIN t_user_user_role_rel rel ON u.user_id = rel.user_id
JOIN t_user_role r ON rel.role_id = r.role_id
WHERE u.tenant_id = :tenantId;

-- ⚠️ 子查询仅在无法用 JOIN 实现时使用
-- ❌ 禁止 SELECT *，必须明确列出字段
-- ❌ 禁止对索引列使用函数（导致索引失效）
```

## 【强制】建表标准模板
```sql
CREATE TABLE t_模块_功能名
(
    功能_id          character varying(32)  NOT NULL,  -- 主键
    功能_name        character varying(50),             -- 名称
    state            character varying(10),             -- 状态：Enable-启用 Disable-禁用
    tenant_id        character varying(50),             -- 租户ID
    create_by        character varying(32),             -- 创建人
    create_time      timestamp without time zone,       -- 创建时间
    last_modify_by   character varying(32),             -- 最后修改人
    last_modify_time timestamp without time zone,       -- 最后修改时间
    CONSTRAINT t_模块_功能名_pkey PRIMARY KEY (功能_id)
) WITH (OIDS=FALSE);

COMMENT ON TABLE  t_模块_功能名          IS '表说明';
COMMENT ON COLUMN t_模块_功能名.功能_id  IS '主键';
COMMENT ON COLUMN t_模块_功能名.state    IS '状态：Enable-启用 Disable-禁用';

CREATE INDEX i_模块_功能名_tenant_id ON t_模块_功能名(tenant_id);
COMMENT ON INDEX i_模块_功能名_tenant_id IS '租户ID索引';
```

## 【强制】变更流程
1. 新建表或修改表结构前，先将数据模型文件发给 DBA 审核确认
2. 将环境变更的 SQL 放到项目约定目录下（如 `src/main/resources/sql`）
3. 脚本命名：`功能名.sql`

## 数据访问规范

```java
// 查询单条（按主键）
Entity entity = dao.load(Entity.class, id);

// 新增
dao.save(entity);

// 更新（全字段）
dao.update(entity);

// 删除
dao.delete(Entity.class, id);
```

## Entity 注解规范

```java
@Data
@Slf4j
public class Entity implements Cloneable, Serializable {

    @Id
    @Column(columnName = "entity_id")
    private String entityId;

    @Column(columnName = "entity_name")
    private String entityName;

    /**
     * 业务种类：TYPE_A / TYPE_B / TYPE_C（注释中说明每个枚举值含义）
     */
    @Column(columnName = "entity_type")
    private String entityType;
}
```

## 分页查询规范
```java
// ✅ 使用项目统一 Page 对象分页
Page page = model.getPage();
// page 内部封装 pageNum / pageSize / total

// ✅ 深分页（offset > 5000）改用游标分页
// 用 entity_id > lastId LIMIT 20 替代 LIMIT 20 OFFSET 10000

// ❌ 禁止不加 LIMIT 的全表查询
// ❌ 禁止在循环中执行 SQL（N+1），改用批量 IN 查询
```

---
> 相关：`logging.md`（日志规范）、`async.md`（异步与上下文）、`distributed-lock.md`（分布式锁）。
