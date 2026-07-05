# Demo 项目索引

本目录存放教程配套的**可运行 demo**。每个 demo 自包含（自带 README + 依赖 + 源码），可独立 clone 运行，对应教程里的某个核心概念。

## Demo 列表

| Demo | 对应教程 | 说明 | 运行 |
|---|---|---|---|
| [ai-test-frame](./ai-test-frame/) | [《AI 自动化测试：方法论与实践》](../assets/ref/AI自动化测试-方法论与实践.html) §8 | 最小可运行的 AI 自动化测试框架（数据驱动 + 注册中心 + 软断言 + 录制转生成思想） | `cd ai-test-frame && python main.py` |
| [ai-metrics](./ai-metrics/) | [阶段 5 · 推广与度量](../pages/stage5.html) | AI 代码占比度量（三层识别算法 + 风格学反伪造）+ 提效同比（Excel 模板） | `cd ai-metrics && python main.py` |
| [report-templates](./report-templates/) | [《汇报材料 AI 生成指南》](../assets/ref/汇报材料-AI生成指南.html) | 5 类汇报 prompt 模板包（PPT/计划书/周报/总结/度量）+ ppt-master 渲染可编辑 PPT | 复制 prompt 填数据 → AI 生成 |
| [role-handbooks](./role-handbooks/) | [《角色操作手册》](../assets/ref/角色操作手册.html) | 4 份角色手册（开发/测试/组长/产品），各含定位+任务+怎么做+工具+清单+坑 | 各级人员拿自己那份照做 |
| [claude-skills](./claude-skills/) | [阶段 4 闭环](../pages/stage4.html) / [阶段 6 沉淀](../pages/stage6.html) | Claude Code skill 集合（团队 Skill 仓库）：devflow 编排型 skill（OpenSpec+Superpowers 6 阶段）+ 统一管理规范 | 复制 skills/ + rules/ 到 .claude/ |
| [handover-templates](./handover-templates/) | [阶段 4 闭环](../pages/stage4.html) / [阶段 5 推广](../pages/stage5.html) | 团队交接协作模板：开发↔测试 / 前后端 / 跨部门（产品↔研发见产品手册） | 按场景挑模板落进工作流 |
| [review-checklists](./review-checklists/) | [阶段 4 闭环](../pages/stage4.html) / [阶段 5 推广](../pages/stage5.html) | 落地验收清单（试点 / 推广）+ 代码审查 checklist（给人看） | 试点结项 / 合并 AI 产出前核对 |

> 后续 demo（RAG 服务、代码知识图谱等）按下方规范追加。

## 新增 Demo 规范

1. 在本目录下新建子目录，命名 **kebab-case**（如 `rag-service`、`code-graph`）
2. 每个 demo **自包含**：
   - `README.md`：运行步骤 + 架构说明 + 思想映射（对应教程哪个概念）
   - `requirements.txt`：独立依赖（不污染教程主站）
   - 源码 + 数据 + 必要的被测对象（让读者 clone 即能跑）
3. 在上方「Demo 列表」表追加一行
4. 教程对应章节加一句指向该 demo 的链接
5. **运行产物分离**：生成的数据/报告/截图等放 demo 内的 `workspace/`（加 `.gitignore` 忽略），与源码分开；自带的被测对象/示例数据保留原位

原则：**任何 demo 都应开箱即跑**——自带被测对象/示例数据，不依赖读者的私有环境。
