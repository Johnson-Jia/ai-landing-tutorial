---
name: perf-diagnosis
description: "性能诊断(诊断型 skill·只读)。定位慢 SQL、内存热点、接口耗时,给结论与建议。触发:慢查询/接口卡/内存高/CPU 飙时排查根因。只读不改动系统。"
license: MIT
metadata:
  author: "Johnson"
  version: "1.0"
---

# 性能诊断技能(诊断型 skill · 只读)

分析性能问题(慢 SQL / 内存热点 / 链路耗时),给结论与建议。**只读,绝不改动系统。**

> 这是「诊断型 skill」的范例——和工具型(连库查数据)、编排型(跑流程)不同,诊断型 skill 的命门是**只读 + 给依据**:只采集、分析、归因、建议,不执行任何变更。变更交给人和 devflow。

## 何时触发

- 用户说「这条 SQL 慢」「接口耗时高」「内存/CPU 飙」「查性能根因」
- AI 拿到 EXPLAIN / 日志 / 指标时,主动归因

## 工作流

### 慢 SQL:解析 EXPLAIN

```bash
python3 ~/.claude/skills/perf-diagnosis/scripts/analyze_slow_sql.py <explain文件>
```

检测全表扫描 / 高成本节点 / 嵌套循环,给索引/JOIN 优化建议。

### 内存 / 链路:见 reference/checklist.md

按清单逐项归因(堆 dump / 火焰图 / 链路 trace)。

## 设计要点

- **只读边界**:脚本只解析输入文本(EXPLAIN/日志),不连库、不执行 SQL、不改配置。安全是诊断型的命门。
- **给依据不给命令**:输出"问题 + 原因 + 建议",不直接"帮你改"——变更走 devflow + 人确认。
- **可复用清单**:`reference/checklist.md` 沉淀诊断方法论,新场景按清单扩展。
