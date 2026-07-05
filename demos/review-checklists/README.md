# 验收与审查清单包

AI 转型过程中的两类把关清单——**落地验收**（试点 / 推广到什么程度算成功）+ **代码审查**（AI 生成代码的人工审查清单）。
对应教程：[阶段 4 闭环试点](../../pages/stage4.html)、[阶段 5 推广度量](../../pages/stage5.html)

## 清单
| 清单 | 用途 | 何时用 |
|---|---|---|
| [落地验收清单.md](./落地验收清单.md) | 试点 / 推广的验收标准 | 单组试点结束、全员推广阶段评估 |
| [代码审查checklist.md](./代码审查checklist.md) | AI 生成代码的人工审查清单 | 每次合并 AI 产出前 |

> 注：给 AI 用的代码审查 skill 在 [claude-skills/code-review](../claude-skills/skills/code-review/)，本包是**给人看**的审查清单，两者互补。

## 使用方式
- 验收清单：作为试点结项 / 推广阶段评审的打分表
- 代码审查 checklist：合并 AI 产出前的逐项核对（关键项用 Hook 强制）

## 与其他模块
- 验收数据来源：[ai-metrics](../ai-metrics/)（AI 占比 / 提效度量）
- 试点工作流：[claude-skills/devflow](../claude-skills/skills/devflow/)
- 交接验收：[handover-templates](../handover-templates/)

## 可单独交付
本目录自包含，可独立作为团队的验收 / 审查规范。
