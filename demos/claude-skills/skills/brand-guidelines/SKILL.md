---
name: brand-guidelines
description: "品牌合规(规范型 skill)。生成或检查 UI/文档是否符合品牌色卡与字体规范。触发:做页面/海报/PPT/组件时检查品牌一致性。含校验器,违规即报。"
license: MIT
metadata:
  author: "Johnson"
  version: "1.0"
---

# 品牌合规技能(规范型 skill · 企业规范 Agent 化)

把企业品牌规范(色卡/字体)编码进 skill,让 AI 输出自动合规,并可校验。

> 这是「规范型 skill」的范例——把"PDF 里的品牌手册"变成"AI 可执行 + 可校验"的规则。AI 生成 UI/文档时自动用品牌色,生成后 `validate_brand.py` 校验,违规即报。

## 品牌规范(示例,实际项目替换为自己的)

- **色卡**:主色 `#1A56DB`(科技蓝)、辅色 `#16A34A`(成功)、强调 `#F59E0B`(警示)、深底 `#0F172A`、白 `#FFFFFF`
- **字体**:中文 `PingFang SC`、英文 `Inter`、等宽 `SF Mono`

## 何时触发

- 用户说「做个页面/海报/PPT/组件」「检查品牌合规」「套品牌色」
- AI 生成含颜色/字体的产物时,主动用本规范

## 工作流

### 生成时(预防)

生成 UI/文档时,颜色只从色卡取,字体只用品牌字体。

### 校验时(把关)

```bash
python3 ~/.claude/skills/brand-guidelines/scripts/validate_brand.py <产物文件>
```

输出违规清单 + 规范依据。退出码 1 表示有违规,接入 CI 可阻断不合规产物。

### 修复时(套色)

```bash
python3 ~/.claude/skills/brand-guidelines/scripts/apply_brand.py <产物文件>
```

把非品牌色替换为最近的品牌色(规范化)。

## 设计要点

- **校验器即规范**:规范不只写在 SKILL.md,还落在 `validate_brand.py` 的白名单里——规范与校验一体,不会"文档说一套、代码做一套"。
- **可接入 CI**:`validate_brand.py` 退出码反映合规性,可作 pre-commit / CI 门禁。
- **企业规范 Agent 化范式**:把色卡/字体换成任何企业规范(文档模板/接口约定/命名规则),同一模式复用。
- **HEX 覆盖范围**:当前 `validate_brand.py` 只校验 6 位 hex(`#RRGGBB`);3 位简写(`#FFF`)、8 位带 alpha(`#RRGGBBAA`)、`rgb()`/`rgba()` 未覆盖。实际项目若用到这些写法,按需扩展 `HEX_RE`(保持白名单统一大小写折叠即可)。
