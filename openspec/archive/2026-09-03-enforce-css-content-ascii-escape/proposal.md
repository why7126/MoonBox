---
purpose: OpenSpec Change Proposal
content: 沉淀 CSS content 非 ASCII 符号 escape 写法治理
created_at: 2026-09-03 09:34:14
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# 沉淀 CSS content 非 ASCII 符号 escape 写法治理

## 背景与动机

需求中心卡片进度分隔符曾通过 CSS 伪元素 `content` 生成，在截图、字体或编码链路中出现过渲染不稳定风险。当前项目已有局部实现使用 `\00B7`，但长期 UI 规则和设计系统校验尚未把“CSS `content` 内非 ASCII 符号统一使用 escape”固化为可执行门禁。

## 变更内容

- 在 `rules/ui-design.md` 沉淀 CSS `content` 生成内容规则：非 ASCII 符号统一使用 CSS escape 写法。
- 扩展 `scripts/validate-design-system.py`，扫描 CSS 文件中的 `content: "..."` / `content: '...'` 字符串，发现原始非 ASCII 字符时报错。
- 增加脚本级单元测试，覆盖原始 `·`、`✓` 失败，以及 `\00B7`、`\2713`、ASCII 和空字符串通过。
- 写入治理迭代日志并更新 spec-logs 索引。

## 影响范围

- UI 规范：`rules/ui-design.md`。
- 设计系统校验：`scripts/validate-design-system.py`。
- 单元测试：`tests/unit/test_validate_design_system.py`。
- OpenSpec：`openspec/changes/enforce-css-content-ascii-escape/`。
- 业务代码：N/A，本 Change 不修改 `src/` 业务实现。
- API/DB/客户端生成/部署/安全：N/A，本 Change 不调整接口、数据模型、客户端生成、部署拓扑或权限边界。
