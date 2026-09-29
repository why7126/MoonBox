---
change_id: fix-requirement-center-bug-card-severity-display
source_bug: BUG-0021-requirement-center-bug-card-severity-display
created_at: 2026-09-14 14:12:36
updated_at: 2026-09-14 14:38:53
---

# 测试计划

## 必跑验证

- `python scripts/validate-root-cause-evidence.py --bug BUG-0021-requirement-center-bug-card-severity-display`
- `python scripts/validate-sprint-scope.py sprint-006 --item BUG-0021-requirement-center-bug-card-severity-display`
- 后端需求中心 API / 构卡相关 pytest。
- 前端需求中心卡片相关 Vitest / Testing Library，包含分级标签 DOM class 与 CSS 等级色彩规则。
- 如响应 schema 影响 OpenAPI / Orval 类型，执行对应生成或校验。

## 验证重点

- BUG 使用 `severity`，REQ 使用 `priority`。
- BUG 不再默认展示 P 值。
- REQ `priority` 与 BUG `severity` 标签在同一分级体系内按等级呈现可区分颜色。
- 缺失或非法 severity 可诊断。
- 独立 Change、文档入口、负责人、Sprint 标签和进度展示不回退。

## 不适用说明

本 Change 不涉及 DB schema、对象存储、部署拓扑、行为埋点或 Task Trace 落地；若实现阶段发现新增观测字段，再补充对应测试。
