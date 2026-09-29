---
bug_id: BUG-0022-requirement-center-html-preview-auth-lost
title: 需求中心卡片 HTML 预览直开受保护接口导致认证失败
decision: approve
created_at: '2026-09-14 15:22:33'
updated_at: '2026-09-14 15:22:33'
reviewed_at: '2026-09-14 15:22:33'
reviewer: 产品团队
severity: medium
---

# 缺陷评审

## 评审结论

批准修复。该缺陷根因已确认，验收清单明确，适合进入 Sprint 规划。

## 评审清单

- [x] 可复现或根因充分：`root-cause.md` 为 `status: confirmed`，包含 6 条可复核证据。
- [x] 严重等级合理：`medium`，阻断 HTML/原型预览工作流，但当前未发现数据丢失、越权或全站不可用证据。
- [x] 回归验收明确：`acceptance.md` 包含 AC-001 至 AC-010，覆盖受控 fetch、Bearer、Blob URL、失败提示、demo 分支和真实浏览器证据。
- [x] 是否需 hotfix 路径：不需要。当前不是 P0/P1 热修，按正常 Sprint 修复链路推进。

## 评审说明

本 BUG 关联 `REQ-0012-frontend-requirement-center`，修复范围集中在需求中心 HTML / prototype 文档预览链路。后续不得绕过 Sprint，批准后下一步先执行 `/sprint-propose --bug BUG-0022-requirement-center-html-preview-auth-lost`，再进入 `/bug-opsx`。
