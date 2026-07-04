# 异常处理规范（通用 rule 模板）

> 异常处理规范：异常体系、全局处理器。放 `.claude/rules/error-handling.md`。

## 异常体系
统一用一个业务异常类（如 `BizException`），配全局异常处理器：
```
RuntimeException
└── BizException（业务异常，带错误信息，WARN 级日志）
```

## 标准抛出
```java
// ✅ 业务校验失败抛业务异常
if (entity == null) {
    throw new BizException("实体不存在");
}
// ✅ 带参数（便于定位）
throw new BizException("订单不存在，id=" + id);

// ❌ 禁止：直接抛 RuntimeException（丢失业务语义）
throw new RuntimeException("xxx");
```

## Controller 层
- 参数校验失败：返回错误响应（如 `Result.error("...")`），**不抛异常**
- 业务异常由**全局异常处理器**统一捕获，Controller 不用手动 try-catch
- 不要把系统异常（堆栈、SQL）直接返回前端

## 空值处理
```java
// ✅ 字符串
if (StringUtils.isBlank(id)) { throw new BizException("ID 不能为空"); }
// ✅ 集合（对外接口返回空集合，不返回 null）
if (CollectionUtils.isEmpty(list)) { return Collections.emptyList(); }
// ✅ 对象
if (Objects.isNull(obj)) { return null; }
// ❌ 禁止对外接口返回 null
```

## 禁止行为
- ❌ 空 catch 块（吞掉异常 = 埋雷）
- ❌ catch 里只 `e.printStackTrace()`（用日志框架 `log.error`）
- ❌ catch 后只打日志不处理——**上层依赖此方法成功就必须 rethrow**
- ❌ 把系统内部异常信息（堆栈、SQL）返回给前端

---
> 相关：`testing.md`（测试规范）、`logging.md`（日志规范）。
