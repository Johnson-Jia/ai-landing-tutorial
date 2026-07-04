---
name: devflow
description: "开发工作流 skill。一条命令从需求到交付：需求探索 → 规范生成 → 计划拆分 → TDD 执行 → 验证 → 归档。编排 OpenSpec 和 Superpowers 两个框架，不重新实现任何逻辑。"
license: MIT
compatibility: 需预装 openspec CLI + Superpowers skills
metadata:
  author: "Johnson"
  version: "3.0"
---

**DevFlow** — 开发工作流 skill。编排 OpenSpec + Superpowers，需求到交付一条命令搞定。编排规则见 `.claude/rules/devflow.md`。

> 这是一个**编排型 skill**——自己不实现任何逻辑，只把 OpenSpec（规范）和 Superpowers（执行）串成 6 阶段流水线。学它的价值不在流程本身，而在 4 个设计手法：①编排不实现 ②恢复判定（断点续传）③覆盖规则（rules 改写底层 skill 默认行为）④渐进式披露（每次只读当前阶段）。

---

## 阶段切换

每个阶段完成后，恢复判定会自动检测文件状态，从正确阶段继续。使用 `/devflow 继续 <change-name>` 即可。

---

## 前置条件检查

触发后**第一件事**检查项目初始化状态：

```bash
ls openspec/          # 检查项目初始化
```

**项目未初始化**时，询问用户：

```
当前项目未初始化 OpenSpec。
是否自动执行 openspec init --tools claude 初始化？(是/手动)
```

用户选"是" → 执行 `openspec init --tools claude && openspec update`，成功后进入 Stage 1。

---

## 恢复判定

中断后按优先级判断恢复点，然后读取对应 Stage 文件执行：

0. **发现变更名**：`ls openspec/changes/` — 扫描活跃变更目录。若用户未提供 `<name>`，据此确定当前变更名。多个活跃变更时询问用户选择。

1. Plan 文件所有 Task 已标记 `[x]` 且无归档 → Stage 5
2. Plan 文件有部分 Task 已标记 `[x]` → Stage 4（从中断处继续，异常处理见 guide）
   - 如有残留 worktree（`git worktree list` 检查）：从 worktree 中未完成 Task 继续
3. `docs/superpowers/plans/` 有计划文件但无 Task 标记 `[x]` → Stage 3，重新生成计划（覆盖）
4. `openspec/changes/<name>/` 有工件但无计划 → Stage 3
5. `openspec/changes/<name>/` 有部分工件（`openspec status --json` 检查）
   - 用户有补充信息 → 编辑已有工件后重新执行 Stage 2
   - 无新信息 → 重新执行 Stage 2，openspec 从 CLI 状态续接
6. `docs/superpowers/specs/` 有设计文档但无 OpenSpec 工件 → Stage 2
7. 以上都没有 → Stage 1

---

## 阶段路由

根据恢复判定或当前进度，**仅读取对应 Stage 文件**：

| 阶段 | 文件 | 调用技能 | 代码图谱工具 |
|------|------|---------|------------|
| Stage 1 | `stages/stage-1.md` | `superpowers:brainstorming` | — |
| Stage 2 | `stages/stage-2.md` | `openspec-propose` | — |
| Stage 3 | `stages/stage-3.md` | `superpowers:writing-plans` | `impact`, `locate` |
| Stage 4 | `stages/stage-4.md` | `superpowers:subagent-driven-development` | 按需 `locate`/`search` |
| Stage 5 | `stages/stage-5.md` | `superpowers:verification-before-completion` | `detect_changes` |
| Stage 6 | `stages/stage-6.md` | `openspec-archive-change` | — |

所有 Stage 文件位于 `stages/` 下。**每次只读取当前执行的 Stage 文件**（渐进式披露）。代码图谱（如 codebase-memory-mcp / code-lens）仅在 Stage 3（影响评估）和 Stage 5（变更验证）强制接入，Stage 4 按需调用，新项目可跳过。

---

## 参考

快速/迷你模式、异常处理、使用示例见 `.claude/skills/devflow/devflow-guide.md`。按需读取，不预加载。
