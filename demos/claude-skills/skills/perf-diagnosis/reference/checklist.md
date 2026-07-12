# 性能诊断清单

## 慢 SQL
1. 拿 EXPLAIN ANALYZE(含实际耗时,非估算)
2. 看"Seq Scan"(全表扫描)→ 加索引 / 检查统计信息
3. 看高 cost 节点 → 优化其子操作
4. 看 Nested Loop 大数据集 → 改 Hash/Merge Join
5. 看 rows 估算 vs 实际偏差大 → ANALYZE 更新统计

## 内存
1. 看堆 dump:大对象 / 集合是否泄漏
2. 看火焰图:热点方法
3. 看缓存:是否无界(LRU/大小限制)

## 接口耗时
1. 看 trace:哪个 span 最长
2. 串行→并行(无依赖步骤)
3. N+1 查询 / 循环内 RPC
4. 锁等待 / GC 停顿
