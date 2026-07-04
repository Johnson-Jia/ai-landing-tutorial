# API 响应规范（通用 rule 模板）

> API 响应规范：统一响应模型包装。放 `.claude/rules/api-response.md`，Controller 返回值自动遵守。

## 核心原则

所有 Controller 方法的返回值**必须用统一的响应模型包装**（如 `Result` / `ApiResponse` / `ResponseEntity`），不要返回裸对象、裸 Map、null，也不要直接 throw 到前端。

> 下方用 `Result` 指代你项目的统一响应模型，按你的技术栈替换。成功用 `Result.ok(...)`，失败用 `Result.error(...)`。

## 成功响应

```java
// 返回数据对象
CourseInfo course = courseService.load(id);
return Result.ok(course);

// 返回分页数据
Page page = model.getPage();
List<CourseInfo> list = courseService.listByPage(page, query);
return Result.ok("success", Map.of(
    "total", page.getTotal(),
    "items", list
));

// 返回简单成功（无数据）
return Result.ok();

// 返回带消息的成功
return Result.ok("操作成功");
```

## 错误响应

```java
// 简单错误消息
return Result.error("参数不能为空");

// 带额外数据的错误（如错误文件下载路径）
Result result = Result.error();
result.setData(Map.of("errorFile", errorFilePath));
return result;

// 带消息和数据
return Result.error("导入失败", errorData);
```

## Controller 层响应模式

### 参数校验失败

```java
if (StringUtils.isBlank(dto.getTitle())) {
    return Result.error("标题不能为空");
}
if (dto.getPeriod() == null || dto.getPeriod() <= 0) {
    return Result.error("时长必须大于 0");
}
```

### 业务校验失败

```java
Entity existing = service.load(id);
if (existing == null) {
    return Result.error("记录不存在");
}
if (!"ACTIVE".equals(existing.getStatus())) {
    return Result.error("只能编辑启用状态的记录");
}
```

### 异常处理

```java
// 业务异常由全局异常处理器统一捕获，无需手动 try-catch
@Override
public Result delete(String id) {
    service.delete(id);
    return Result.ok("删除成功");
}

// 需要向用户返回特定错误信息时，再捕获
try {
    service.importData(list);
    return Result.ok("导入成功");
} catch (BusinessException e) {
    log.error("[XxxImport] 导入失败", e);
    return Result.error("导入失败：" + e.getMessage());
}
```

## 异步任务响应

```java
// 异步任务立即返回任务对象（不要同步阻塞等结果）
Task task = service.exportAsync(filter);
return Result.ok(task);

// 查询任务状态
Task task = taskService.getLastByType(type);
if (task == null) {
    return Result.ok();
}
return Result.ok(task);
```

## 禁止行为

```java
// ❌ 直接抛异常给前端（应返回 error 或交全局处理器）
throw new RuntimeException("记录不存在");

// ❌ 返回 null
return null;

// ❌ 返回裸 Entity（应转 DTO/VO）
return entity;

// ❌ 返回复杂对象而不包装
return new HashMap<>() {{ put("x", y); }};
// ✅ 应包装
return Result.ok(Map.of("x", y));

// ❌ Controller 方法上加 @Transactional（事务归 Service）
@Transactional
public Result save(...) { ... }

// ❌ catch 后只打日志不处理
catch (Exception e) {
    log.error("xxx", e);
    // 必须返回错误响应，或继续抛出
}
```

## 快速参考

| 场景 | 响应方式 |
|------|----------|
| 查询成功（单条） | `Result.ok(entity)` |
| 查询成功（列表） | `Result.ok(list)` |
| 查询成功（分页） | `Result.ok("success", map)` |
| 操作成功（无返回） | `Result.ok()` |
| 参数校验失败 | `Result.error("xxx不能为空")` |
| 业务规则失败 | `Result.error("xxx不存在")` |
| 异步任务 | `Result.ok(task)` |
| 带额外数据的错误 | `Result.error()` + `setData()` |

---
> 相关：`service-dao.md`（事务归 Service + Controller 分层）、`error-handling.md`（异常处理）。
