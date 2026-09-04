---
purpose: OpenSpec Change Design
content: CSS content 非 ASCII escape 写法治理设计
created_at: 2026-09-03 09:34:14
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# 设计说明

## 治理策略

CSS `content` 主要用于伪元素、计数器或辅助装饰文本。对分隔点、箭头、勾号等非 ASCII 符号，直接写入原始字符会把渲染稳定性暴露给文件编码、字体 fallback、截图链路和压缩工具。治理策略是允许继续使用 CSS 生成内容，但非 ASCII 符号必须转为 CSS escape。

## 校验设计

- 扫描范围沿用设计系统校验脚本的 `src/web/src` 与 `src/shared`。
- 仅对 `.css` 文件中的 `content: "..."` 与 `content: '...'` 字符串做检查，避免误伤 `justify-content`、`align-content` 和 TypeScript 数据字段。
- 字符串内容包含任意 `ord(char) > 127` 的原始字符时报告违规。
- `\00B7`、`\2713` 等 escape 写法保持 ASCII 字符序列，校验通过。
- `content: ""`、`content: "*"`、`attr()`、`counter()` 等不属于非 ASCII 原始符号的用法不阻断。

## 非目标

- 不自动改写业务 CSS。
- 不新增前端构建链路。
- 不限制 DOM 文案、Markdown 内容或 TypeScript 普通字符串中的中文和符号。
- 不改变现有 Design System token、组件视觉和运行时代码。
