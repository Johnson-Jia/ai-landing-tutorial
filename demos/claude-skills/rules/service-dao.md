# Service 层与 DAO 层规范（通用 rule 模板）

> Service 层与 DAO 层规范：接口与实现分离 + 事务归 Service + DAO 不含业务逻辑。放 `.claude/rules/service-dao.md`。

## 分层职责

| 层 | 职责 | 禁止 |
|---|---|---|
| Controller | 参数校验、调 Service、包装响应 | 写业务逻辑、直接调 DAO、加事务 |
| Service | 业务逻辑、事务控制 | 调外部 HTTP / 发 MQ（事务内） |
| DAO | 数据访问（CRUD / SQL） | 写业务判断 |

## Service 接口定义（API 模块）

```java
// 位置：api 模块，对外只暴露接口
public interface CourseInfoService {

    /** 保存或修改 */
    String saveOrUpdate(CourseInfo entity);

    /** 删除，返回删除数量 */
    Integer delete(String id);

    /** 按ID查询，不存在返回 null */
    CourseInfo load(String id);
}
```

## Service 实现（实现模块）

```java
@Service
@Slf4j
public class CourseInfoServiceImpl implements CourseInfoService {

    @Autowired
    private CourseInfoDAO courseInfoDAO;

    // 解决循环依赖用 @Lazy
    @Lazy
    @Autowired
    private RelatedService relatedService;

    @Override
    public String saveOrUpdate(CourseInfo entity) {
        if (StringUtils.isBlank(entity.getId())) {
            entity.setId(UUID.randomUUID().toString());
            courseInfoDAO.insert(entity);
            log.info("[CourseInfoService] 创建成功, id={}, title={}",
                     entity.getId(), entity.getTitle());
        } else {
            courseInfoDAO.update(entity);
            log.info("[CourseInfoService] 更新成功, id={}", entity.getId());
        }
        return entity.getId();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Integer delete(String id) {
        CourseInfo entity = courseInfoDAO.load(id);
        if (entity == null) {
            throw new BusinessException("记录不存在");
        }
        return courseInfoDAO.delete(id);
    }
}
```

## DAO 层规范

```java
@Repository
@Slf4j
public class CourseInfoDAO {

    @Autowired
    protected NamedParameterJdbcTemplate jdbcTemplate;

    // 方式1：ORM / 简单 CRUD（用你项目的 ORM，如 JPA / MyBatis-Plus）
    public CourseInfo load(String id) { /* ... */ }
    public void insert(CourseInfo e) { /* ... */ }
    public void update(CourseInfo e) { /* ... */ }

    // 方式2：JdbcTemplate，用于复杂查询
    public List<CourseInfo> listByCategory(String categoryId) {
        String sql = """
            SELECT id, title, status
            FROM t_example
            WHERE category_id = :categoryId
              AND is_deleted = 0
            ORDER BY create_time DESC
            """;
        return jdbcTemplate.query(sql,
            Map.of("categoryId", categoryId),
            new BeanPropertyRowMapper<>(CourseInfo.class));
    }
}
```

## 事务使用规范

```java
// ✅ 事务放 Service 层，粒度尽量小，rollbackFor = Exception.class
@Transactional(rollbackFor = Exception.class)
public void assign(String userId, String planId) {
    assignDAO.insert(buildRecord(userId, planId));
    scoreDAO.addScore(userId, planId);
    // 禁止在此调用外部 HTTP / RPC 接口或发 MQ——长耗时操作撑大事务、易超时回滚
}

// ❌ 事务方法为 private（AOP 代理不生效）
@Transactional
private void doAssign() { ... }

// ❌ 同类内部调用事务方法（绕过代理，事务不生效）
public void assign() {
    this.doAssign();
}

// ❌ 自调用导致事务失效时，注入自身代理或抽到另一个 Service
```

## 禁止行为

- ❌ DAO 层包含业务逻辑判断（业务归 Service）
- ❌ `SELECT *`，必须明确列出字段
- ❌ 循环内执行 SQL（N+1 问题），改批量查询
- ❌ 事务方法为 private 或被同类自调用
- ❌ 事务内调用外部 HTTP / RPC / 发 MQ 消息
- ❌ Service 实现里写 SQL（SQL 归 DAO）

---
> 相关：`batch.md`（批量操作）、`naming.md`（命名）、`api-response.md`（响应包装）。
