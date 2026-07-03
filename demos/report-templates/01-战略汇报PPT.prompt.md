# 战略汇报 PPT · AI 生成 prompt

## 用途
向管理层（老板/高层）汇报 AI 转型的**背景、目标、路线图、阶段性成果、资源请求**。
适合：立项汇报、阶段性进展汇报、要资源/要预算。

## 你要准备的数据
- **背景**：为什么转（行业/内部压力），1-2 句
- **量化目标**：产出提升 / AI 占比 / 交付周期 / Bug 率，具体数字
- **路线图**：分阶段（如 6 阶段：总纲→启动→赋能→设施→试点→推广）
- **已有成果**（若有试点）：AI 占比、产出提升、Bug 下降等数据
- **资源请求**：工具预算 / 培训投入 / 人力 / 考核绑定
- **你的角色**：转型负责人 / 技术总监 / ...

## Prompt（复制下面的内容，填入你的数据，发给 AI）

```
你是一位资深的技术战略顾问，擅长把 AI 转型讲清楚、说服管理层。请根据我提供的数据，生成一份《AI 战略转型汇报 PPT》，用 Marp Markdown 格式（可一键渲染成 PPT）。

格式要求：
1. 开头用这个 frontmatter：
---
marp: true
theme: report-blue
paginate: true
---
2. 封面页用 <!-- _class: cover --> 标记
3. 章节结构（每节 1-2 页，要点精炼）：
   - 封面：主标题 + 副标题 + 汇报人
   - 为什么转：现状/压力（3-4 个要点）
   - 转型目标：用表格列量化目标
   - 路线图：分阶段（每阶段一行，精炼）
   - 阶段性成果：已有数据用引用块(>)高亮关键数字
   - 资源请求：工具/培训/人力/考核
   - 请求批准页（用 <!-- _class: chapter --> 章节页样式）
4. 风格：每页 3-5 个要点，数据用表格或引用块，避免大段文字

数据（请用我提供的真实数据替换方括号占位）：
- 背景：[填你的转型背景]
- 目标：[填你的量化目标，如人均产出+50%、AI占比≥70%]
- 路线图：[填你的分阶段计划]
- 已有成果：[填试点数据，如 AI占比76.6%、产出+104%、Bug-16pp；没有就写「即将试点验证」]
- 资源请求：[填你要的资源]
- 我的角色：[填你的角色]

请直接输出 Markdown 全文，不要解释。
```

## 渲染成 PPT
内容生成后，在 **Claude Code** 里用 [**ppt-master**](https://github.com/hugohe3/ppt-master) skill 生成**原生可编辑 PPTX**（不是图片式 PPT，PowerPoint 里每个元素都能改）。

**工作流**：
1. 把 AI 输出的汇报内容存为 `.md`
2. 安装 ppt-master（一次性）：
   ```bash
   git clone https://github.com/hugohe3/ppt-master.git
   cd ppt-master && pip install -r requirements.txt
   ```
3. 在 Claude Code 里 `@hugohe3/ppt-master`，说「**用这份战略汇报内容生成 PPT**」
4. AI 按 ppt-master 的 `SKILL.md` 工作流，生成原生可编辑 `.pptx`

> **关键**：PPT 类汇报用 ppt-master 生成原生可编辑 PPTX（DrawingML 形状/文本框），AI 生成内容 → ppt-master 生成精美 PPT，不用手画。ppt-master 的 [`examples/`](https://github.com/hugohe3/ppt-master) 目录有 20+ 精美可编辑 deck 可参考。
