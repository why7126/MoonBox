---
review_id: REV-REQ-0036-001
requirement_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除 - 评审结论
date: 2026-09-15
participants:
  - product
result: approved
created_at: 2026-09-15 23:16:40
updated_at: 2026-09-15 23:16:40
---

# 需求中心文档抽屉简化与 Change 属性模块移除 - 评审结论

## 评审结论

通过评审。REQ-0036 的范围清晰：删除需求中心右侧文档抽屉中的整个“Change 追溯属性”模块，保留文档属性与正文，并要求多 Change 关联及 Change 文档仍通过抽屉外入口可达。

该需求是 REQ-0026 的体验 refinement，不改变父需求已交付的 Change 可见性、关联识别、阶段映射、任务进度语义、权限和文档读取边界。优先级 P2 合理，适合进入后续 Sprint 规划。

## 评审清单

- [x] 范围清晰，Out of Scope 明确：不新增独立 Change 编辑、任务勾选、阶段流转、归档执行能力，不重做卡片布局和统计口径。
- [x] 验收标准可测试：覆盖模块不存在、文档属性与正文、单/多 Change 文档可达、权限回归、响应式和 computed style 证据。
- [x] 优先级与依赖合理：P2，依赖 REQ-0026 已交付能力，仅做阅读体验与信息架构收敛。
- [x] UI 类实现策略已决：已有 prototype/web/context.md 与 prototype.html，后续 Change 需补 UI Skeleton 和视觉证据。
- [x] 无与现有 REQ 重复未说明：明确为 REQ-0026 refinement，不改写父需求交付状态。
- [x] 观测声明完整：已声明 product_data_collection_observability 为 not_applicable，并说明不影响 API、DB、请求日志、行为事件、Task Trace、对象存储或请求封装。

## 条件通过项

- [ ] 后续 OpenSpec Change 设计必须延续“直接删除抽屉内 Change 属性模块”的结论，不得将同名或等价模块迁移为抽屉内新折叠区。
- [ ] 实施阶段必须补齐 1440px 与窄视口、深浅主题、长标题/长 ID/长正文的视觉证据。
- [ ] 实施阶段必须记录关键 computed style 或等价检查，覆盖文档属性区 padding、border、gap、font-size、line-height、正文顶部间距和抽屉滚动容器 overflow。
- [ ] 实施阶段必须回归单 Change、多 Change、独立 Change、无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL。

## 风险与处置

| 风险 | 等级 | 处置 |
|---|---|---|
| 删除抽屉模块后多 Change 文档入口不可达 | 中 | 在 Change 设计中明确抽屉外入口承接位置，并用验收 AC 覆盖单/多 Change |
| 文档属性与正文顶部出现残留间距或断层 | 中 | 以截图和 computed style 作为验收证据 |
| 权限边界因入口调整被放宽 | 中 | 保持现有文档 API 和对象授权，加入权限回归 |

## 评审结果

```yaml
result: approved
issue_status_after_review: approved
next_step: /sprint-propose --req REQ-0036-requirement-center-document-drawer-simplification
```
