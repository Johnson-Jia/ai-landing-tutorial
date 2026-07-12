# 慢 SQL 诊断样例

## EXPLAIN 输入
```
Seq Scan on public.orders  (cost=0.00..50000.00 rows=1000000)
  Filter: (status = 'PAID')
```

## 诊断结果
- [seq_scan] 全表扫描 orders
  → 考虑在 status 列加索引
- [high_cost] 总成本 50000
  → 优先优化过滤条件
