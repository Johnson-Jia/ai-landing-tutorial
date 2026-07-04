# 系统日志规范（通用 rule 模板）

> 系统日志规范：日志门面、级别、格式、敏感信息处理。放 `.claude/rules/logging.md`，AI 写日志时自动遵守。

## 【强制】禁止使用 System.out / System.err

```java
// ❌ 错误
System.out.println("xxx");
System.err.println("xxx");

// ✅ 正确
log.info("xxx", e);
log.error("xxx", e);
```

## 【强制】禁止使用 e.printStackTrace()

```java
// ❌ 错误
} catch (Exception e) {
    e.printStackTrace();
}

// ✅ 正确
} catch (Exception e) {
    log.error("xxx", e);
}
```

## 【强制】禁止直接使用 Log4j / Logback API，统一使用 SLF4J

```java
// ❌ 错误
import org.apache.log4j.Logger;
import ch.qos.logback.classic.Logger;

// ✅ 正确
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
```

## 【强制】禁止在日志中明文记录敏感信息
禁止记录：身份证号、银行卡号、密码、手机号、Token 等。

```java
// ❌ 错误
log.info("用户登录, userId={}, password={}", userId, password);

// ✅ 正确
log.info("用户登录, userId={}", userId);
```

## 【推荐】统一使用 Lombok @Slf4j 声明日志对象

```java
// ❌ 不推荐（冗余）
private static final Logger logger = LoggerFactory.getLogger(Foo.class);

// ✅ 推荐
@Slf4j
public class EntityServiceImpl {
    public void load() {
        try {
            // do something
        } catch (Exception e) {
            log.error("加载失败", e);
        }
    }
}
```

## 【推荐】使用占位符，禁止字符串拼接

```java
// ❌ 错误：字符串拼接，无论日志级别是否开启都会执行拼接，影响性能
log.debug("Processing trade with id: " + id + " and symbol: " + symbol);

// ⚠️ 多余：SLF4J 占位符已做懒加载，不需要手动 isDebugEnabled 判断
if (log.isDebugEnabled()) {
    log.debug("Processing trade with id: " + id + " and symbol: " + symbol);
}

// ✅ 正确：使用占位符，未开启该级别时不执行参数拼接
log.debug("Processing trade with id: {} and symbol: {}", id, symbol);
```

## 日志级别规范

| 级别    | 使用场景                                              |
|---------|---------------------------------------------------|
| `DEBUG` | 详细调试信息，生产环境默认关闭（`logging.level.root=info`） |
| `INFO`  | 关键业务节点（业务对象创建、记录写入、任务分配、状态变更）    |
| `WARN`  | 可预期的业务异常（参数非法、数据不存在、状态不符等）          |
| `ERROR` | 系统异常、需立即排查的问题，必须附完整异常堆栈               |

## 标准写法

```java
@Slf4j
@Service
public class EntityRecordServiceImpl implements EntityRecordService {

    // ✅ 关键业务节点 - 格式：[类名] 描述, key=value
    log.info("[EntityRecord] 记录写入成功, entityId={}, userId={}, progress={}",
             entityId, userId, progress);

    // ✅ 外部服务调用 - 记录入参和耗时
    long start = System.currentTimeMillis();
    // ... RPC / HTTP 调用 ...
    log.info("[EntityRecord] 调用用户服务获取用户信息完成, userId={}, cost={}ms",
             userId, System.currentTimeMillis() - start);

    // ✅ 异常日志 - 必须传入异常对象（打印完整堆栈）
    log.error("[EntityRecord] 记录写入失败, entityId={}, userId={}, error={}",
              entityId, userId, e.getMessage(), e);

    // ✅ 业务预期异常 - 用 WARN
    log.warn("[EntityRecord] 业务对象不存在, entityId={}", entityId);

    // ❌ 字符串拼接（高并发下有性能问题）
    log.info("记录写入成功, entityId=" + entityId);

    // ❌ 异常未传入，丢失堆栈
    log.error("写入失败: " + e.getMessage());

    // ❌ 打印敏感信息
    log.info("用户登录, userId={}, token={}", userId, token);
}
```

## 日志前缀约定
格式：`[ClassName]` 或 `[ClassName#methodName]`（方法名可选，适合同类多方法区分）

```java
log.info("[TaskPlanService] ...");
log.info("[TaskPlanService#assign] ...");
```

## 配置说明
```properties
# application.properties 示例（按项目实际调整）
logging.path=./logs
logging.level.root=info
```

---
> 相关：`database.md`（数据库规范）、`error-handling.md`（异常处理）、`async.md`（异步与上下文）。
