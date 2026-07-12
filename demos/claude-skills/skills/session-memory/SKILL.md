---
name: session-memory
description: "会话记忆(记忆型 skill)。长对话/超长任务超出上下文时,结构化压缩历史,保留用户纠正与关键决策。触发:对话太长要续接/上下文要清/跨会话记关键。"
license: MIT
metadata:
  author: "Johnson"
  version: "1.0"
---

# 会话记忆技能(记忆型 skill · 跨会话/超长对话)

把长对话结构化压缩成 SESSION_MEMORY,保留关键信息,供续接新会话。

> 这是「记忆型 skill」的范例——解决长任务/跨会话的上下文丢失问题。核心是**结构化压缩 + 优先级**:不是无差别摘要,而是按"用户纠正 > 错误 > 活跃工作 > 已完成"的优先级,确保关键信息不丢。

## 何时触发

- 对话接近上下文上限,需要压缩后继续
- 跨会话续接任务(把上次的关键带过来)
- 用户说"压缩一下""总结会话""清上下文但要记关键"

## 工作流

### 无 API key:生成压缩 prompt

```bash
python3 ~/.claude/skills/session-memory/scripts/compress.py <对话文件>
```

输出结构化压缩 prompt,交给当前 AI 或新会话执行。

### 有 API key:真调 LLM 压缩

```bash
ANTHROPIC_API_KEY=... python3 ~/.claude/skills/session-memory/scripts/compress.py <对话文件> --compress
```

## 结构(优先级从高到低)

1. **用户意图**:用户想达成什么
2. **用户纠正**:用户修改/否决过的(权重最高,保留原话,防回退)
3. **错误与修正**:踩过的坑、已修正的错误
4. **活跃工作**:当前正在做的
5. **已完成**:可最简
6. **待办**:还没做的
7. **关键引用**:重要文件/链接/数据

## 设计要点

- **优先级即设计**:用户纠正放最前——模型最易"回退到旧行为",保留原话是防回退的关键(源自 cookbooks session_memory_compaction 实测)。
- **prompt 即产物**:无 key 时也能用(输出 prompt),降低门槛;有 key 时一键真压缩。
- **范式可迁移**:把"会话"换成"项目交接/工单流转",同一压缩模式复用。
