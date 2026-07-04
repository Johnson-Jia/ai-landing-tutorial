# 测试规范（通用 rule 模板）

> 测试规范：命名、结构、禁止行为。放 `.claude/rules/testing.md`，AI 写测试时自动遵守。

## 基本原则
- 测试放 `src/test/java/`，与生产代码同包
- 类命名 `XxxTest`，方法命名 `test_{方法名}_{场景}`
- JUnit 5 + Spring Boot Test（或你框架的测试支持）

## 结构：Given-When-Then
每个测试**只测一个场景**，用 Given-When-Then 组织：
```java
@Test
void test_save_success() {
    // Given：准备数据
    Entity e = new Entity();
    e.setName("test");
    // When：执行
    String id = service.save(e);
    // Then：断言
    assertNotNull(id);
}
```

## 命名规范
| 场景 | 命名示例 |
|---|---|
| 正常流程 | `test_save_success` |
| 参数为空 | `test_save_nullParam` |
| 数据不存在 | `test_delete_notFound` |
| 边界条件 | `test_list_largeOffset` |
| 异常情况 | `test_save_duplicateKey` |

## 测试数据准备
- `@BeforeEach` 重置环境（测试间不共享状态）
- 复杂场景用 `@Sql`（或你框架的数据初始化）准备数据，测完清理

## 禁止行为
- ❌ 连生产数据库（用测试库 / H2 / testcontainers）
- ❌ `System.out.println`（用日志框架）
- ❌ 没有断言的测试
- ❌ 测试之间有依赖（必须能独立运行、任意顺序）
- ❌ 跳过失败的测试而不修复

## 推荐做法
- ✅ 每个方法一个场景
- ✅ Given-When-Then 结构
- ✅ 方法名清楚描述场景
- ✅ 测试与生产代码一起提交、一起 Review

---
> 相关：`service-dao.md`（Service 层规范）、`error-handling.md`（异常处理）。
