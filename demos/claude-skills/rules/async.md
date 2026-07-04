# 异步与线程规范（通用 rule 模板）

> 异步与线程规范：线程池、上下文透传、消息队列解耦、定时任务幂等。放 `.claude/rules/async.md`，AI 写异步代码时自动遵守。

## 线程池使用原则
- ✅ 统一使用项目中已定义的线程池 Bean（注入使用）
- ❌ 禁止使用 `Executors` 工厂方法（无界队列有 OOM 风险）
- ❌ 禁止在方法内部局部 new 线程池（无法统一治理）
- 不同业务域使用隔离的线程池，禁止共用一个池

## 线程池配置参考（核心参数方法论）

```java
// 在项目统一的配置类中集中定义线程池 Bean（不要散落在各业务类）

@Bean("taskExecutor")
ThreadPoolTaskExecutor taskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(cpuCount * 2);
    executor.setMaxPoolSize(cpuCount * 4);
    executor.setQueueCapacity(2500);
    executor.setRejectedExecutionHandler(new ThreadPoolExecutor.DiscardPolicy());
    return executor;
}

@Bean("bizExecutor")  // 业务隔离的线程池
ThreadPoolTaskExecutor bizExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(cpuCount * 2);
    executor.setMaxPoolSize(cpuCount * 2);
    executor.setQueueCapacity(2100);
    executor.setRejectedExecutionHandler(new ThreadPoolExecutor.DiscardPolicy());
    return executor;
}
```
> 参数按业务实际调整，遵循"按业务域隔离"原则，非必要不新增线程池。

## 线程池使用规范

```java
@Autowired
@Qualifier("taskExecutor")
private ThreadPoolTaskExecutor taskExecutor;

// 提交任务前先捕获调用方的上下文，在异步线程内重新设置（上下文不自动透传）
Map<String, String> contextMap = ContextHolder.getNewContextMap();
taskExecutor.submit(() -> {
    log.info("[EntityService] 线程池任务开始执行, entityId={}", dto.getEntityId());
    // 在异步线程内重新设置上下文
    ContextHolder.setContextMap(contextMap);
    try {
        doWork(request);
    } catch (Exception e) {
        log.error("[EntityService] 线程池任务执行失败", e);
    }
});

// ❌ 禁止裸用 @Async（默认 SimpleAsyncTaskExecutor 无池化，每次新建线程）
@Async
public void asyncPush(EntityPushDTO dto) { ... }
```

## 消息队列使用规范（异步解耦场景优先用 MQ）

```java
// ✅ 不需要关注执行结果的跨服务通知，优先用 MQ 而非线程池
@Autowired
private RocketMQTemplate rocketMQTemplate;

Map<String, String> msgMap = new HashMap<>(4);
msgMap.put("entityId", entityId);
msgMap.put("action", String.valueOf(action));
msgMap.put("functionCode", Constants.ENTITY_NOTIFY);
MessageEvent<Map<String, String>> event = new MessageEvent<>(ContextHolder.getNewContextMap(), msgMap);
rocketMQTemplate.convertAndSend(Constants.ENTITY_NOTIFY, JsonUtil.obj2Json(event));
```

## 定时任务规范（以 XXL-Job 为例，方法论通用）

```java
// ✅ 定时任务必须有幂等保护，避免重复执行；按需决定是否遍历所有租户
@XxlJob("syncEntityDuration")
public void syncEntityDuration() {
    String param = XxlJobHelper.getJobParam();
    StringBuilder errorMsg = new StringBuilder();
    boolean hasError = false;

    try {
        // 获取目标范围（统一入口）
        List<String> tenantIds = getTargetTenants(param);

        // 遍历处理
        for (String tenantId : tenantIds) {
            try {
                ContextHolder.setTenantId(tenantId);
                // 具体业务
            } catch (Exception e) {
                hasError = true;
                log.error("[syncEntityDuration] tenantId={} error", tenantId, e);
                errorMsg.append("tenantId=")
                        .append(tenantId)
                        .append(" error: ")
                        .append(e.getMessage())
                        .append("\n");
            } finally {
                // 重置上下文，避免污染下一次循环
                ContextHolder.setContextMap(null);
            }
        }

    } catch (Exception e) {
        log.error("[syncEntityDuration] job error", e);
        XxlJobHelper.handleFail("job error: " + e.getMessage());
        return;
    }

    // 统一出口
    if (hasError) {
        XxlJobHelper.handleFail(errorMsg.toString());
    } else {
        XxlJobHelper.handleSuccess();
    }
}

private List<String> getTargetTenants(String param) {
    if (StringUtils.isNotBlank(param)) {
        return Arrays.stream(param.split(","))
                .map(String::trim)
                .filter(StringUtils::isNotBlank)
                .distinct()
                .collect(Collectors.toList());
    }
    return getAllActiveTenants();
}
```

## 禁止行为
- ❌ 禁止异步任务吞掉异常（必须有 catch + log.error）
- ❌ 禁止在异步任务中直接使用调用方的 `ContextHolder`（线程上下文不传递，必须先捕获再 set）
- ❌ ThreadLocal 用完必须在 finally 中 `remove()`，防止内存泄漏
- ❌ 禁止裸用 `@Async` 而不指定线程池（无池化）

---
> 相关：`logging.md`（日志规范）、`distributed-lock.md`（分布式锁）、`database.md`（数据库规范）。
