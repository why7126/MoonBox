---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
reviewed_at: 2026-09-14 11:03:16
reviewer: 产品团队
decision: approve
severity: medium
---

# 缺陷评审

## 评审结论

批准修复。

## 评审清单

- [x] 可复现或根因充分：用户截图证明卡片误报；目标 Change trace 存在 `## 验证摘要`；后端识别逻辑未覆盖该标题。
- [x] 严重等级合理：`medium`。问题影响治理看板可信度和验收判断，但未证明破坏源文件、权限或真实归档流程。
- [x] 回归验收明确：`acceptance.md` 已列出 `AC-001` 至 `AC-005`，覆盖标题兼容、既有来源、安全边界和页面展示。
- [x] hotfix 路径：不需要。可按正常 Sprint 纳入修复。

## 依据

- 根因状态：`confirmed`
- 根因证据：4 条可复核证据，包含截图、目标 Change trace、后端识别代码路径和测试覆盖缺口。
- 验收重点：扩展独立 Change trace 验收来源标题识别，至少覆盖 `验证摘要`，并保持显式引用安全边界。

## 后续门禁

该 BUG 后续已纳入 sprint-006，创建 OpenSpec Change，并完成实现与归档。
