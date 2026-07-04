# Stage 6: 归档

## 前置条件检查

```bash
# 1. 确认 tasks.md 全部完成（Stage 5 已验证，此处二次确认）
cat openspec/changes/<change-name>/tasks.md | grep -c "\- \[ \]"
# 输出应为 0（无未勾选项）

# 2. 确认 working tree 状态
git status -s
# 所有变更文件应已暂存或待提交
```

若 tasks.md 有未勾选项 → 退回 Stage 5。

## Step 1: 询问归档方式

```
Stage 5 验证通过。选择归档方式：
1. 归档 + commit — 先归档变更，再 git commit
2. 只归档 — 仅归档变更，不 commit
```

用户确认后按以下顺序执行。

## Step 2: 清理残留 worktree

```bash
git worktree list
```

如有残留 worktree → 清理后再继续。

## Step 3: 执行归档（必须完成）

调用 **`openspec-archive-change`** 归档变更：
- delta spec 同步时选择"立即同步"
- 归档目标：`openspec/changes/archive/YYYY-MM-DD-<name>/`

**归档验证（不可跳过）：**

```bash
# 确认归档目录已生成
ls openspec/changes/archive/YYYY-MM-DD-<change-name>/

# 确认源目录已移除
ls openspec/changes/<change-name>/
# 应返回 "No such file or directory" 或为空
```

若归档目录不存在或源目录未移除 → **归档未完成，不可继续 commit。** 排查原因后重试。

## Step 4: Commit（仅当用户选方案 1）

**仅在 Step 3 归档验证通过后执行：**

使用 `git commit` 提交变更（或你的 `/commit` 命令）。

验证 commit：

```bash
git log --oneline -1
git status -s
# 应无未提交文件
```

## 完成输出

```
DevFlow 完成。
- Change: <change-name>
- 归档: openspec/changes/archive/YYYY-MM-DD-<name>/
- Commit: <commit hash>（或：未 commit）
```
