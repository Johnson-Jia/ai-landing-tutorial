# DevFlow 编排规则

> 始终生效，不可被任何 Skill 内部指令覆盖。冲突时以本规则为准。
>
> 这是 devflow 的「覆盖规则」——底层 skill（brainstorming / openspec-propose 等）各有默认行为，devflow 通过本规则**改写它们的出口和边界**，把 6 个独立 skill 串成一条流水线。这是「编排型 skill」的核心手法：不重新实现，只覆盖。

## 覆盖规则

> 以下 "Step N" 均指**原始技能的内部步骤编号**，不是 devflow 的 Stage 编号。

### brainstorming  (原始技能内部 9 步)
- 完成后**进入 Stage 2 (openspec-propose)**，不进入 writing-plans
  > 覆盖原 Step 9 "Transition to implementation → 调用 writing-plans" 的出口重定向
- Step 6 的 **commit 被覆盖**，仅保存文件
  > 覆盖原 Step 6 "Write design doc → commit"，将 commit 统一到 Stage 6

### opsx:propose  (openspec-propose 技能)
- 接收 Stage 1 设计文档作为输入，**不主动询问开放式问题**
- **允许在关键信息缺失时澄清具体细节**（如技术选型、接口约定、数据结构）
- 完成后**不要建议运行 /opsx:apply**，下一步是 writing-plans
  > 覆盖原出口 "Run /opsx:apply to start working on the tasks"

### writing-plans  (原始技能内部 5 步)
- 输入来源是 **OpenSpec 的 design.md + specs/**，不读取 brainstorming 设计文档
  > 覆盖原输入源，改为读取 Stage 2 产出的 OpenSpec 工件
- **不反向更新 tasks.md**
- **Execution Handoff 被覆盖**，不提供选择，直接进入 Stage 4
  > 覆盖原 Step 5 "提供 subagent-driven / inline 两选项"

### subagent-driven  (原始技能内部 12 步)
- 进度追踪只更新 **Plan 文件** Task checkbox，**不更新 tasks.md**
- **验证通过前禁止 commit 主分支**
  > 覆盖原 implementer-prompt 中 "Commit your work"：
  > - 串行路径：子代理在主分支工作，跳过 commit，由协调者在 Stage 6 统一 commit
  > - 并行路径：worktree 内完成，合并回主分支时 squash 不提交
- 覆盖原技能的 `using-git-worktrees` REQUIRED 要求：**仅在并行路径使用 worktree**
  > 两级执行策略：
  > - 串行 → 主分支直接执行，不 commit（有依赖 / 文件重叠 / 不值得并行）
  > - 并行 → worktree 隔离，完成后 squash 合并（无依赖 + 无文件重叠 + 值得并行）
- Step 12 "finishing-a-development-branch" **被覆盖**，Stage 4 后进入 Stage 5
  > 覆盖原 Step 12 的出口，改为进入验证阶段

## 禁止事项

- 不要跳过任何 Stage
- 不要替 Skill 做它的工作
- 不要在验证通过前 commit 主分支
- 并行分派 SubAgent 时，仅限无依赖且无文件重叠的 Task
- 不要为串行任务创建 worktree
