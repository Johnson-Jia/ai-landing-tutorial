# 批量操作规范（通用 rule 模板）

> 批量操作规范：批量代替循环、IN 分批、N+1 消除。放 `.claude/rules/batch.md`。

## 核心原则

**永远用一次批量操作代替循环内单条操作**。N+1 是后端性能第一杀手：循环里查 / 改 N 次，就是 N 次连接 + N 次往返。

## 批量查询

### 【强制】IN 子句用命名参数

```java
// ✅ IN 子句批量查询（命名参数防 SQL 注入）
Set<String> ids = new HashSet<>(Arrays.asList("id1", "id2", "id3"));
String sql = "SELECT id, name, status FROM t_example WHERE id IN (:ids)";
List<Map<String, Object>> list = jdbcTemplate.queryForList(
    sql, Map.of("ids", ids));
```

### 【推荐】IN 子句超 500 条分批

```java
// ✅ 分批查询（每批 500），避免单 SQL 过大 / 数据库 IN 列表上限
List<Xxx> batchQuery(Set<String> allIds) {
    List<Xxx> results = new ArrayList<>();
    int batchSize = 500;
    List<String> idList = new ArrayList<>(allIds);
    for (int i = 0; i < idList.size(); i += batchSize) {
        List<String> batch = idList.subList(i, Math.min(i + batchSize, idList.size()));
        results.addAll(doBatchQuery(batch));
    }
    return results;
}

private List<Xxx> doBatchQuery(List<String> ids) {
    String sql = "SELECT id, name FROM t_example WHERE id IN (:ids)";
    return jdbcTemplate.queryForList(sql, Map.of("ids", ids), Xxx.class);
}
```

### 【强制】禁止循环内单条查询（N+1）

```java
// ❌ 循环内单条查询——每次都建立连接
for (String id : ids) {
    list.add(service.load(id));
}

// ✅ 批量查询后 Map 缓存，循环里只查内存
Map<String, Xxx> map = service.getMap(ids);
for (String id : ids) {
    Xxx x = map.get(id);
    if (x != null) list.add(x);
}
```

## 批量更新

### 【强制】循环内直接走 DAO/SQL，不要调 Service

```java
// ✅ 循环内直接 update（简单场景），不要绕回 Service
void batchUpdateTitle(List<Map<String, String>> updateList) {
    String sql = "UPDATE t_example SET title = :title, " +
            "last_modify_by = :modifyBy, last_modify_time = NOW() " +
            "WHERE id = :id";
    for (Map<String, String> args : updateList) {
        jdbcTemplate.update(sql, Map.of(
            "title", args.get("title"),
            "modifyBy", currentUserId(),
            "id", args.get("id")
        ));
    }
    log.info("[XxxService] 批量更新完成, count={}", updateList.size());
}
```

### 【推荐】大批量分批提交

```java
// ✅ 大批量：每 500 条一批，便于追踪进度、控制事务大小
void batchUpdateLarge(List<Xxx> list) {
    int batchSize = 500;
    for (int i = 0; i < list.size(); i += batchSize) {
        List<Xxx> batch = list.subList(i, Math.min(i + batchSize, list.size()));
        doBatchUpdate(batch);
        log.info("[XxxService] 批量更新进度, {}/{}",
            Math.min(i + batchSize, list.size()), list.size());
    }
}
```

### 【强制】禁止循环内调 Service 更新

```java
// ❌ 循环内调 Service——每次都可能触发事务、日志、AOP 等额外开销
for (Xxx item : items) {
    service.update(item);
}
// ✅ 循环内直接调 DAO/SQL
for (Xxx item : items) {
    dao.update(item);
}
```

## 批量插入

```java
// ✅ 循环 + 单条 insert（或用 ORM 批量保存 / JdbcTemplate.batchUpdate）
void batchInsert(List<Xxx> list) {
    String sql = "INSERT INTO t_example (id, name, status, create_time) " +
            "VALUES (:id, :name, :status, NOW())";
    for (Xxx item : list) {
        jdbcTemplate.update(sql, Map.of(
            "id", UUID.randomUUID().toString(),
            "name", item.getName(),
            "status", "ACTIVE"
        ));
    }
    log.info("[XxxService] 批量插入完成, count={}", list.size());
}
```

## 批量删除

```java
// ✅ 用 IN 子句，一次删完
void batchDelete(List<String> ids) {
    String sql = "DELETE FROM t_example WHERE id IN (:ids)";
    jdbcTemplate.update(sql, Map.of("ids", ids));
    log.info("[XxxService] 批量删除完成, count={}", ids.size());
}
```

## 禁止行为汇总

| 行为 | 原因 | 正确做法 |
|------|------|----------|
| 循环内单条查询 | N+1，性能差 | 批量查询 + Map 缓存 |
| 循环内调 Service | 事务/日志开销 | 循环内直接调 DAO/SQL |
| IN 子句超量不分批 | 数据库限制 / 性能 | 每 500 条一批 |
| 批量操作无日志 | 无法追踪 | 记录数量 + 进度 |

## 快速参考

| 操作 | 推荐方式 | 分批阈值 |
|------|----------|----------|
| 批量查询 | IN 子句 + 命名参数 | 500 |
| 批量更新 | 循环 + 单条 update | 500 |
| 批量插入 | 循环 + 单条 insert / batchUpdate | 500 |
| 批量删除 | IN 子句 | 500 |

---
> 相关：`service-dao.md`（DAO 分层）、`database.md`（字段规范）。
