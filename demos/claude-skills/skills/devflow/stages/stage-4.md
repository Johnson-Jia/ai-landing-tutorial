# Stage 4: TDD + 分阶段审查 → `superpowers:subagent-driven-development`

## 上下文

```
使用 superpowers:subagent-driven-development 执行计划。

计划文件: docs/superpowers/plans/YYYY-MM-DD-<change-name>.md
```

## 执行流程

### 第一步：构建执行 DAG

读取 Plan 文件所有 Task 的元信息（标题、Dependencies、Files），构建依赖有向无环图：

- **依赖判定**：
  - Task A 修改的文件被 Task B 读取/依赖 → A 必须先于 B
  - 两个 Task 修改不同文件且无数据流依赖 → 可并行候选
  - 无法确定时默认串行（宁串勿错）

- **分批规则**：按拓扑排序分批，同一批内 Task 无依赖关系

### 第二步：并行可行性分析

对同一批内的并行候选 Task，用 **Files** 字段做重叠检查：

```
对每对并行候选 Task (A, B)：
  overlap = A.Files ∩ B.Files
  若 overlap 非空 → 标记为冲突，降级为串行
```

文件重叠 = 即使无显式依赖也不能并行（同一文件的编辑冲突不可避免）。

### 第三步：按策略分派执行

| 执行策略 | 触发条件 | 执行方式 |
|---------|---------|---------|
| **串行** | 有依赖 / 文件重叠 / 批次仅 1 个 Task | 主分支逐 Task 执行，不 commit |
| **并行** | 无依赖 + 无文件重叠 + Task 值得并行 | 各 SubAgent 独立 worktree，完成后合并 |

**不值得并行的信号**：Task 仅涉及单文件微调、步骤 ≤ 3 步。这类任务并行的 worktree 开销大于收益，归入串行。

**降级**：worktree 创建失败时，回退为串行执行。

### SubAgent 内部规范

每个 SubAgent（无论哪种策略）：
- Plan 已包含精确文件路径（来自 Stage 3 的 locate），直接 Read 源码
- 执行过程中对照 `openspec/changes/<change-name>/specs/` 验证实现
- 如需定位 Plan 中未覆盖的代码，按需调用代码图谱 locate / search
- **不 commit**（commit 统一到 Stage 6）

**串行路径**：主分支直接工作，跳过 commit。

**并行路径**：worktree 内完成工作，协调者执行 `git merge --squash` 合并回主分支（暂存不提交），清理 worktree。

### 第四步：标记进度

同一批全部完成后，将 Plan 文件中对应 `### Task N: title` 标记为 `### [x] Task N: title`。

### 第五步：最终审查

全部 Task 完成后做最终全量代码审查。

## 完成

汇报 Plan 文件 Task 完成状态（N/N completed）。用户确认 → Stage 5。
