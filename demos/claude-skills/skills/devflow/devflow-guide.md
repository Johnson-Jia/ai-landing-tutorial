# DevFlow 参考指南

> 按需加载，不随 Skill 自动加载。SKILL.md 指向本文件时读取对应章节。

---

## 快速模式

### 标准快速模式（2-3 个任务）

用户说"快速模式"：

```
Stage 1 brainstorming（精简版：跳过视觉辅助、跳过方案对比）
Stage 2 opsx:propose
Stage 3 writing-plans（仍保留，subagent-driven 需要 Plan 文件）
Stage 4 subagent-driven
Stage 5 verification
Stage 6 archive
```

**不跳过 writing-plans**。subagent-driven-development 需要 Plan 文件。快速模式的"快"体现在 brainstorming 和 writing-plans 的精简，而非跳过 Stage。

### 迷你模式（1 个任务）

用户说"迷你模式"时，合并前三个 Stage：

```
Stage 1+2+3 合并 → Stage 4 subagent-driven → Stage 5 verification → Stage 6 archive
```

**升级机制**：brainstorming 后发现以下任一条件时暂停，建议切换标准模式：
- 任务数 > 3
- 横跨 2 个以上技术领域（如同时涉及前端+后端+数据库）

已生成工件保留不重做。用户坚持则继续。

**合并步骤**：
1. `superpowers:brainstorming` 快速分析（跳过视觉辅助、方案对比、扩展思考）
2. 基于分析结果调用 `openspec-propose` 生成工件
3. 基于 tasks.md 用 `superpowers:writing-plans` 生成精简 Plan（1 任务 = 2-4 step）
4. 一次性汇报，用户确认后进入 Stage 4

**示例**：

```
用户: /devflow 迷你模式 给 User 模型添加 phone 字段

DevFlow: [前置检查 ✓]
         [Stage 1+2+3 合并执行]
         迷你模式准备完成：
         - 任务: 1 个（User 模型添加 phone 字段）
         - 计划: 3 个 step
         开始执行？(继续/修改)

用户: 继续

DevFlow: [Stage 4 → Stage 5 → Stage 6]
         DevFlow 完成。
```

---

## 异常处理

| 情况 | 处理 |
|------|------|
| brainstorming 发现需求过于复杂 | 建议拆分为多个独立子需求，各自启动 devflow |
| openspec-propose 中断无新信息 | 重新执行 Stage 2，openspec 从 CLI 状态续接 |
| openspec-propose 中断需补充信息 | 先编辑已有工件，再重新执行 Stage 2 |
| opsx:propose 工件不完整 | 直接编辑工件后继续 |
| writing-plans 中断需补充信息 | 补充信息后重新执行 Stage 3，覆盖已有计划文件 |
| writing-plans 有 TODO/占位符 | 要求重写对应 step |
| subagent-driven 任务间中断 | 从 Plan 文件中下一个未标记 `[x]` 的 Task 继续 |
| subagent-driven 任务内中断（有残留代码） | `git stash` 保留进度，询问用户选择：重新开始（丢弃 stash）或恢复继续（stash pop） |
| subagent-driven 遇到阻塞 | 使用 `superpowers:systematic-debugging` |
| verification 中断后恢复 | 重新执行 Stage 5（幂等操作，安全重跑） |
| verification 验证失败 | 回 Stage 4 修复 |
| 实现中发现规范有误 | 更新 OpenSpec 工件后继续（OpenSpec 支持 fluid 更新） |

---

## 使用示例

### 标准流程

```
用户: /devflow 开发用户认证系统，支持邮箱注册、JWT、密码加密

DevFlow: [前置检查 ✓]
         [Stage 1: brainstorming → 设计文档已保存]
         Stage 1 完成。建议 change-name: user-auth
         继续？(继续/修改)

用户: 继续
DevFlow: [Stage 2: openspec-propose → 工件已生成]
         Stage 2 完成。8 个任务。
         继续？(继续/修改)

用户: 继续
DevFlow: [Stage 3: writing-plans → 计划已生成]
         Stage 3 完成。32 个 step。
         继续？(继续/修改)

用户: 继续
DevFlow: [Stage 4: subagent-driven → 逐任务执行 + 两阶段审查]
         Stage 4 完成。
         继续？(继续)

用户: 继续
DevFlow: [Stage 5: verification → 验证通过]
         Stage 5 完成。执行 commit 和归档？(继续)

用户: 继续
DevFlow: [commit + Stage 6: archive]
         DevFlow 完成。
```
