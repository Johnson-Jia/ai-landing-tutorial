# 汇报材料 Prompt 模板包

用 AI 一键生成 AI 转型的各类汇报材料（PPT / 计划书 / 周报 / 总结 / 度量报告）。
对应教程：[《汇报材料 AI 生成指南》](../../assets/ref/汇报材料-AI生成指南.html)

## 工作流（4 步）
```
1. 准备数据    整理你的真实数据（产出/AI占比/Bug/进展...）
2. 复制 Prompt 打开对应 .prompt.md，复制 Prompt，填入数据
3. 发给 AI    任意 AI（Claude / ChatGPT / GLM）→ 生成汇报内容（Markdown）
4. 渲染       PPT 类 → ppt-master 生成原生可编辑 PPTX；文档类 → 直接用 / 转 PDF
```

## 5 类模板
| 模板 | 用途 | 输出格式 |
|---|---|---|
| [01-战略汇报PPT](./01-战略汇报PPT.prompt.md) | 向老板汇报进展 / 要资源 | **可编辑 PPTX** |
| [02-转型计划书](./02-转型计划书.prompt.md) | 立项审批 | 文档 |
| [03-周报](./03-周报.prompt.md) | 关键节点跟踪 | 文档 |
| [04-阶段总结报告](./04-阶段总结报告.prompt.md) | 结项 / 晋升述职 | 文档 |
| [05-效果度量报告](./05-效果度量报告.prompt.md) | 数据证明提效（可接 ai-metrics） | 文档 |

## PPT 渲染（战略汇报 PPT 用）

PPT 类汇报生成的是 Markdown 内容，用 [**ppt-master**](https://github.com/hugohe3/ppt-master)（GitHub 开源，MIT，1.6万 stars）生成**原生可编辑的 PPTX**。

### 工作流
report-templates 的 Prompt 负责生成**汇报内容**（Markdown）→ 在 Claude Code 里用 **ppt-master skill** 把内容生成精美可编辑的 `.pptx`。

```
report-templates（Prompt 包）→ AI 生成汇报内容（MD）
                                        ↓
                              Claude Code + ppt-master skill
                                        ↓
                              原生可编辑 PPTX（DrawingML 形状/文本框）
```

### 为什么是 ppt-master（根本原因）
**Marp / Slidev 导出的 PPTX 是图片式（不可编辑）；ppt-master 生成的是原生 DrawingML（可编辑）。** 这是选它的根本原因：

- **Marp / Slidev**：把每页幻灯片渲染成图片再塞进 PPTX → 在 PowerPoint 里无法改任何元素（文字、形状、图表都是图）
- **ppt-master**：基于 `python-pptx` 生成原生 PowerPoint 的 DrawingML 结构 → 每个**形状、文本框、图表、动画都是独立可编辑元素**，PowerPoint 里能改每一个细节，不是图片

### 安装 ppt-master
```bash
git clone https://github.com/hugohe3/ppt-master.git
cd ppt-master
pip install -r requirements.txt
```

### 用法（在 Claude Code 里）
ppt-master 是一个 **Claude Code 的 harness / 工作流 skill**，在 Claude Code 里通过 `@hugohe3/ppt-master` 引用：

1. 用 report-templates 的 Prompt 生成汇报内容（Markdown）
2. 在 Claude Code 里 `@hugohe3/ppt-master`，对它说「**用这份战略汇报内容生成 PPT**」
3. AI 按 ppt-master 的 `SKILL.md` 工作流，把内容生成原生可编辑的 `.pptx`

> 更多示例见 ppt-master 的 [`examples/`](https://github.com/hugohe3/ppt-master) 目录（20+ 精美可编辑 deck）。

## 为什么是 Prompt 包，不是工具
- **用任意 AI**：不绑定 Claude Code/特定工具，读者用 ChatGPT/Claude/GLM 都行
- **prompt 是内容资产**：可单独交付、可独立卖；工具是可选渲染层，可替换
- **可复制**：拿 prompt + 自己数据，照做即生成，不靠「灵感」

## 可单独交付
本目录自包含（5 个 prompt + 本说明），可独立打包分发/售卖。PPT 渲染用外部开源项目 [ppt-master](https://github.com/hugohe3/ppt-master)，按需指引安装即可。
