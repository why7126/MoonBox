---
created_at: 2026-08-10 09:05:11
updated_at: 2026-08-10 09:05:11
owner: MoonBox 产品团队
change_id: add-issues-changelog-index
---

# 设计说明

## 设计原则

全局事件索引只回答“最近有哪些 REQ/BUG 生命周期事件”，不回答“当前权威状态是什么”。当前状态仍由 `_registry.yaml` 与单条 Issue `trace.md` 负责，交付事实仍由 Sprint 四件套和 OpenSpec Change 负责。

## 目录设计

```text
issues/requirements/
├── _registry.yaml
├── CHANGELOG.md
├── plan/
├── review/
└── archive/

issues/bugs/
├── _registry.yaml
├── CHANGELOG.md
├── plan/
├── review/
└── archive/
```

`CHANGELOG.md` 固定保留在对应根目录，不随单条 Issue 在 `plan/review/archive` 间迁移。

## 记录模型

REQ 表字段：

```text
时间 | 事件 | REQ | 标题 | 状态 | 阶段 | 关联 Sprint | 关联 Change | 摘要 | 后续建议
```

BUG 表字段：

```text
时间 | 事件 | BUG | 标题 | 严重等级 | 状态 | 阶段 | 关联 Sprint | 关联 Change | 摘要 | 后续建议
```

事件类型固定为：`capture`、`generate`、`complete`、`review.approve`、`review.reject`、`review.defer`、`sprint.include`、`opsx.create`、`apply.done`、`archive.done`、`status.sync`、`trace.fix`。

## 维护策略

- capture/generate/complete/review/opsx/sprint/apply/archive 等命令在完成关键生命周期事件后维护对应全局索引。
- 普通文案润色、格式调整、错别字修复、非状态性验收措辞调整可不记录。
- 条目必须按时间倒序追加，并遵守公开安全边界。

## 风险与控制

- 风险：全局索引被误用为事实源。
- 控制：规则、技能和 delta spec 均明确它只是摘要入口，状态判断仍读取 `_registry.yaml`、`trace.md`、Sprint 和 OpenSpec。

- 风险：BUG 索引复制日志或复现原文导致隐私泄露。
- 控制：BUG `CHANGELOG.md` 只允许一句话摘要，禁止复制日志、截图个人信息或未脱敏复现原文。
