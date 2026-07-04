# 分布式锁规范（通用 rule 模板）

> 分布式锁规范：Redisson 实现、锁粒度、超时、释放。放 `.claude/rules/distributed-lock.md`，AI 写并发控制代码时自动遵守。

## 基本原则
- 统一使用 **Redisson** 实现分布式锁，禁止自行用 SETNX / SET EX 实现
- 锁粒度尽量小，只锁核心业务段，不锁整个方法
- 必须设置等待超时和持有超时，禁止无限等待

## 标准模板

```java
@Autowired
private RedissonUtils redissonUtils;

// ✏️ 替换业务 key：租户 + 用户 + 业务唯一标识
RLock lock = redissonUtils.getLock("lock:" + tenantId + ":" + userId + ":" + entityId);
boolean acquired = false;
try {
    // waitTime=10s（等待获锁时间）, leaseTime=300s（持有锁最长时间）
    acquired = lock.tryLock(10, 1, 300, TimeUnit.SECONDS);
    if (!acquired) {
        throw new BizException("系统繁忙，请稍后重试");  // ✏️ 替换为项目异常类
    }
    // ---- 业务逻辑 ----

} catch (InterruptedException e) {
    log.error("====== InterruptedException =======", e);
    Thread.currentThread().interrupt();
    throw new BizException("获取锁被中断");
} finally {
    if (acquired && lock.isHeldByCurrentThread()) {
        lock.unlock();
    }
}
```

## 锁 Key 命名规范
格式：`lock:<tenantId>:<userId>:<唯一标识>`

| 示例 Key                     | 说明      |
|----------------------------|---------|
| `lock:t001:u12345:order-67890` | 下单锁   |
| `lock:t001:u12345:entity-abc`  | 业务对象操作锁 |

> 命名应包含足够的维度信息，保证锁粒度精准，避免误锁其他用户的同类操作。

## 禁止行为
- ❌ 禁止在 `@Transactional` 事务方法内部加分布式锁
  （原因：锁释放时事务可能尚未提交，其他线程读到旧数据）
- ❌ 禁止不判断 `isHeldByCurrentThread()` 直接调用 `unlock()`
- ❌ 禁止 `waitTime` 设为 0 且不处理获锁失败的情况
- ❌ 禁止锁粒度为整张表级别的操作
- ❌ 禁止忽略 `InterruptedException`（必须 `Thread.currentThread().interrupt()` 恢复中断标志）

---
> 相关：`async.md`（异步与线程）、`database.md`（数据库事务）、`error-handling.md`（异常处理）。
