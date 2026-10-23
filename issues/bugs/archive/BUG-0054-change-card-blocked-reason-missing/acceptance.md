---
bug_id: BUG-0054-change-card-blocked-reason-missing
title: 纯 Change 卡片验收阻塞缺少具体原因验收标准
created_at: '2026-10-20 18:56:49'
updated_at: 2026-10-21 19:17:28
owner: 产品团队
severity: medium
acceptance_status: passed
---

# 纯 Change 卡片验收阻塞缺少具体原因验收标准

## 验收范围

以下为修复交付门禁，已按本次证据逐项验证；根因确认与缺陷文档校验不能算作修复通过。两条关联 BUG 分别验收，保留原有 Change、Sprint 与归档门禁。

### AC-001 已知阻塞可操作

- [x] AC-001：输入缺失和内容变化分别显示中文摘要，能定位受影响 AC、安全相对路径及建议操作，不仅显示 blocked。
- 验证方式与证据：诊断结构单测、卡片投影测试及真实页面各分支截图。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-002 未执行与未知原因兜底

- [x] AC-002：未执行验收显示补充验收提示；无法分类的错误显示原因待核查及证据入口，不伪造具体缺失原因。
- 验证方式与证据：隔离样本覆盖两个分支，页面或组件证据。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-003 诊断链路保持一致

- [x] AC-003：readiness 到归档准入、卡片 acceptance_blocked_reason 与 action.disabled_reason 的语义一致，页面摘要和禁用动作提示不冲突。
- 验证方式与证据：端到端字段对照和真实部署交互证据。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-004 提示不改变准入

- [x] AC-004：blocked 时动作继续禁用；ready 时恢复可用且不残留旧阻塞提示。
- 验证方式与证据：状态切换自动测试与刷新后的浏览器证据，不实际归档业务样本。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

### AC-005 输出脱敏

- [x] AC-005：提示和可见诊断中不出现本机绝对路径、密钥、配置原文或原始堆栈；合法仓库相对路径可展示。
- 验证方式与证据：含敏感占位输入的负向测试，泄漏字段数为 0。
- 当前结果：通过；命令回归、真实部署与浏览器证据见关联 Change verification.md。

## 量化记录

记录每项 AC 的通过/失败、首次执行与复验耗时、总命令耗时、工具失败次数、修复前后误阻塞或无详情样本数。Token 仅使用可归属的实际采集值；缺失标记 unavailable，不估算。无既有性能基线，不虚设改善百分比；固定样本与环境后对照。修复效果以全部 AC 通过和真实部署观察为准。

## 观测与安全边界

product_data_collection_observability: N/A，本次仅制定验收文档，无新产品采集。affected_layers: 治理验收读取、归档准入、需求中心卡片。validation: 根因证据与中文标题校验、Workflow Sync；修复执行时重新判断 API/UI/部署/安全及客户端生成影响。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-21 19:17:28
accepted_by: workflow-sync
source_change: fix-change-card-blocked-reason
source_sprint: sprint-011
evidence: [openspec/archive/2026-10-20-fix-change-card-blocked-reason/evidence/acceptance/20261020192451515211-2985d172/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

