# Stage 5: 验证 → `superpowers:verification-before-completion`

## 前置校验

逐 Task 校验代码变更是否匹配任务规格，这是验证的核心基础：

```
1. 读取 Plan 文件，遍历每个 Task（已标记 [x] 的）

2. 逐 Task 进行代码校验：
   a. 读取该 Task 的步骤描述，提取预期变更内容
   b. 读取该 Task 的 Capability 字段，找到对应的
      openspec/changes/<name>/specs/<capability>/spec.md 作为校验基准
   c. 对 Task 的 Files 字段中的文件，检查 git diff：
      - 预期修改的文件是否有实际变更
      - 实际变更的代码是否覆盖了 spec 中该 capability 的所有需求点
      - 是否存在预期外的变更（修改了不该改的文件/函数）
   d. 有自动化测试则运行，验证 Task 范围内的测试通过

3. 汇总校验结果：
   - 全部通过 → 更新 tasks.md（基于 Plan 的 Capability 去重生成的完成状态）
   - 存在失败 → 报告具体 Task 及不匹配项，退回 Stage 4
```

若 Plan 中存在未标记 `[x]` 的 Task → 直接退回 Stage 4。

## 代码图谱辅助

> 新项目时跳过本节，直接进入验证部分。
> 代码图谱指 codebase-memory-mcp / code-lens 这类代码知识图谱 MCP（见教程阶段 3 基础设施）。

验证阶段用代码图谱做文件级变更影响评估，作为最终安全网：

```
detect_changes → repo="仓库名" scope="all"
— 评估变更文件的爆炸半径（受影响符号、执行流）
— 检查 risk：LOW 可继续，MEDIUM/HIGH/CRITICAL 需在验证结果中说明
```

## 验证

```
使用 superpowers:verification-before-completion 验证以下声明：

验证项：
1. Plan 文件所有 Task 已完成 — 无未标记的 ### Task N
2. 所有测试通过 — 有自动化测试则运行，无则提示用户手动验证
3. 代码符合 design.md — 对照 openspec/changes/<name>/design.md
4. 代码符合 proposal.md — 对照 openspec/changes/<name>/proposal.md
5. 无 lint/type 错误 — 运行对应检查命令
6. 无提前 commit — git log 检查：
   - 如发现异常 commit，报告列表（hash、message、时间）
   - 询问用户是否 git reset --soft HEAD~N，确认后执行
7. 变更影响可控 — 代码图谱 detect_changes 风险评估结果

<代码图谱 detect_changes 结果>

规范位置: openspec/changes/<change-name>/
```

## 路由

验证通过 → 读取 `stages/stage-6.md`。验证失败 → 报告不成立的声明，回 Stage 4 修复。
