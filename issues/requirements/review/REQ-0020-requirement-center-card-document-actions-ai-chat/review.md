---
review_id: REV-REQ-0020-001
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
date: 2026-08-18
participants:
  - product
result: approved
created_at: 2026-08-18 09:51:13
updated_at: 2026-08-18 09:51:13
---

# 需求评审

## 评审结论

REQ-0020 评审通过。需求范围聚焦前台需求中心卡片文档查看、阶段动作流转、全局 AI 聊天抽屉、导入校验、tasks 进度抽屉、受限验收与归档详情跳转，非目标和工作流门禁已明确。

## 评审检查清单

- [x] 范围清晰，Out of Scope 明确。
- [x] 验收标准可测试，覆盖功能 AC、Prototype UI AC 和安全边界。
- [x] 优先级与依赖合理，依赖 REQ-0012 页面骨架与 REQ-0013 真实数据接入。
- [x] UI 类原型策略已决，`prototype/web/` 已包含 HTML、PNG、SVG 和拆解 context。
- [x] 与现有 REQ 的关系已说明：作为 REQ-0012 / REQ-0013 后续增强，不重复替代父需求。

## 条件通过项

- [ ] `/req-opsx` 阶段必须在 Change `design.md` 写入 UI Contract 和 UI Skeleton，并引用 `trace.md` 中的 `prototype_refs` 与 `knowledge_base_refs`。
- [ ] 纳入 Sprint 后，Sprint 规划需保留 Prototype UI Gate、1440px 视觉验收、Mock/API 边界和文件安全异常分支任务。
- [ ] 实现不得绕过 REQ/BUG 评审、Sprint 纳入、OpenSpec apply/archive 等既有门禁。

## 下一步

`/sprint-propose --req REQ-0020-requirement-center-card-document-actions-ai-chat`
