# Stage 2: 规范生成 → `openspec-propose`

## 上下文

```
使用 openspec-propose 技能创建变更 "<change-name>"。

需求已通过 brainstorming 完成，完整设计文档：
docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md

请先读取上述设计文档完整内容，基于其中所有需求要点生成 OpenSpec 工件。
不要摘要或压缩设计文档内容，确保所有需求细节完整传递。

如果设计文档中缺少生成 OpenSpec 工件所需的关键技术细节（如接口约定、数据结构、技术选型），应主动澄清这些具体信息。
```

## 产出

`openspec/changes/<change-name>/` 下：proposal.md, design.md, specs/, tasks.md

## 完成

汇报工件列表和 capability 数。然后**引导用户审查任务粒度**：

```
## Stage 2 完成

工件列表：proposal.md, design.md, specs/, tasks.md
Capability 数：N 个

### 任务粒度审查

请检查 specs/ 中的 capability 拆分是否合理：

- 每个 capability 应该是可独立验证的功能单元（不是"做所有事"）
- capability 之间应该低耦合、可独立实现
- 如果某个 capability 满足以下任一条件，考虑拆分：
  - 横跨 3 个以上独立的技术领域（如同时涉及数据库+API+前端）
  - 需要 2 个以上不同角色的开发者才能独立验证
  - 描述中出现 3 个以上并列的"且"连接的需求点
- 如果多个 capability 强依赖同一个文件且无法并行，考虑合并

是否需要调整？(确认/调整)
```

用户选择调整 → 协助编辑 specs/ 目录和 tasks.md，调整完成后重新确认。

如果满足以下**全部条件**，建议快速模式：
- capability 数 ≤ 3
- 单一技术领域（如纯后端 / 纯前端 / 纯配置变更）
- proposal.md 中 "What Changes" 段落 ≤ 5 个要点

用户确认 → Stage 3。
