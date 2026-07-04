# 命名与项目结构规范（通用 rule 模板）

> 命名与项目结构规范：类后缀约定 + 方法动词前缀 + 目录分层 + import 顺序。放 `.claude/rules/naming.md`。

## 类命名规范

| 类型 | 命名规则 | 示例 |
|---|---|---|
| Controller | `XxxController` | `OrderController` |
| Service 接口 | `XxxService` | `OrderService` |
| Service 实现 | `XxxServiceImpl` | `OrderServiceImpl` |
| DAO / Repository | `XxxDAO` / `XxxRepository` | `OrderDAO` |
| Entity | `Xxx`（无后缀） | `Order` |
| DTO | `XxxDTO` | `OrderPushDTO` |
| VO | `XxxVO` | `OrderDetailVO` |
| Model（请求入参） | `XxxModel` / `XxxRequest` | `OrderQueryModel` |
| 枚举 | `XxxEnum` | `OrderStatusEnum` |
| 常量类 | `XxxConstants` | `BizConstants` |
| 配置类 | `XxxConfig` | `RedisConfig` |

## 方法命名规范

| 操作 | 前缀 | 示例 |
|---|---|---|
| 查询单个 | `load / get / find` | `loadOrder()` |
| 查询列表 | `list / query` | `listByCategory()` |
| 分页查询 | `page / queryPage` | `pageOrderList()` |
| 新增 | `save / add / create` | `saveOrder()` |
| 更新 | `update / modify` | `updateStatus()` |
| 删除 | `delete / remove` | `deleteOrder()` |
| 批量操作 | `batch` + 操作 | `batchDelete()` |
| 统计 | `count / stat` | `countRecord()` |
| 检查 | `check / validate` | `checkExists()` |

## 目录分层

### API 模块（接口定义层，对外发布）

```
api/
└── {module}/
    ├── domain/      ← Entity
    ├── dto/         ← DTO
    ├── service/     ← Service 接口
    ├── constant/    ← 常量
    └── enums/       ← 枚举
```

### 实现模块

```
impl/
└── {module}/
    ├── controller/  ← XxxController
    └── service/
        ├── XxxServiceImpl.java
        └── dao/     ← XxxDAO
├── model/           ← 请求入参模型
├── config/          ← 配置类
├── common/          ← 公共组件
├── event/           ← 事件处理
└── util(s)/         ← 工具类
```

> 包名按你项目的组织包，关键是**按 module 分包 + 按层分目录**，不要按层扁平堆所有 module。

## import 顺序

组间空一行，按以下顺序：

1. 标准库（`java.*` / `javax.*`）
2. 第三方库（`org.*` / `com.google.*` / `io.*` 等）
3. 项目内部包
4. `static` 静态导入

## 禁止行为

- ❌ 通配符导入：`import com.example.*`
- ❌ 未使用的 import
- ❌ Service 层 import Controller 层的类（依赖方向反了）
- ❌ 直接把 Entity 暴露给接口层（必须转 DTO/VO）

---
> 相关：`service-dao.md`（分层职责）、`api-response.md`（DTO/VO 包装）。
